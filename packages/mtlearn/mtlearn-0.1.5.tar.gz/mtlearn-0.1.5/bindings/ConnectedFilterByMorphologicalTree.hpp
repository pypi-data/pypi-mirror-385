#pragma once


#include <mmcfilters/attributes/AttributeComputedIncrementally.hpp>
#include <mmcfilters/trees/NodeMT.hpp>
#include <mmcfilters/trees/MorphologicalTree.hpp>
#include <mmcfilters/utils/Common.hpp>

#include "MorphologicalTreePybind.hpp"
#include "PybindTorchUtils.hpp"

#include <memory>
#include <vector>
#include <tuple>

#include <pybind11/pybind11.h>
#include <torch/extension.h>



namespace mtlearn {

namespace py = pybind11;

using mmcfilters::AttributeComputedIncrementally;
using mmcfilters::InvalidNode;
using mmcfilters::MorphologicalTreePybindPtr;
using mmcfilters::MorphologicalTreePybind;
using mmcfilters::NodeId;

class ConnectedFilterByMorphologicalTree {
public:

    static torch::Tensor filtering(MorphologicalTreePybindPtr tree, torch::Tensor sigmoid) {
        int numRows = tree->getNumRowsOfImage();
        int numCols = tree->getNumColsOfImage();
        int n = numRows * numCols;
        float* sigmoid_ptr = sigmoid.data_ptr<float>();
        
        std::unique_ptr<float[]> mapLevel(new float[tree->getNumNodes()]);

        for (NodeId nodeId : tree->getNodeIds()) {
            float residue = static_cast<float>(tree->getResidueById(nodeId));

            if (tree->getParentById(nodeId) != InvalidNode) {
                mapLevel[nodeId] = mapLevel[tree->getParentById(nodeId)] + (residue * sigmoid_ptr[nodeId]);
            }
            else{
                mapLevel[nodeId] = residue * sigmoid_ptr[nodeId];
            }
        }

        auto out = torch::empty({numRows, numCols}, torch::kFloat32);
        float* imgOutput = out.data_ptr<float>();
        for (NodeId nodeId : tree->getNodeIds()) {
            for (int pixel : tree->getCNPsById(nodeId)) {
                imgOutput[pixel] = mapLevel[nodeId];
            }
        }

        return out;
    }


    static std::tuple<torch::Tensor, torch::Tensor> gradients(MorphologicalTreePybindPtr treePtr, torch::Tensor attrs, torch::Tensor sigmoid, float beta_f, torch::Tensor gradientOfLoss) {
        float* attributes = attrs.data_ptr<float>();
        float* sigmoid_ptr = sigmoid.data_ptr<float>();
        MorphologicalTreePybind* tree = treePtr.get();
        int rows = attrs.size(0); // numNodes
        int cols = attrs.size(1); // numFeatures
        torch::Tensor gradFilterWeights = torch::empty({rows * cols}, torch::kFloat32);
        torch::Tensor gradFilterBias = torch::empty({rows}, torch::kFloat32);

        float* gradFilterWeights_ptr = gradFilterWeights.data_ptr<float>();
        float* gradFilterBias_ptr = gradFilterBias.data_ptr<float>();

        std::unique_ptr<float[]> localDerivativeOfFilterOutput(new float[tree->getNumNodes()]);
        for (NodeId nodeId : tree->getNodeIds()) {
            float dSigmoid = sigmoid_ptr[nodeId] * (1 - sigmoid_ptr[nodeId]);
            float residue = tree->getResidueById(nodeId);
            // float residue = tree->getParentById(nodeId) != InvalidNode ? tree->getResidueById(nodeId) : 0;

            // Calcula o gradiente local para cada nó
            localDerivativeOfFilterOutput[nodeId] = residue * dSigmoid * beta_f;

            // Calcula o gradiente do filtro para os pesos e bias
            gradFilterBias_ptr[nodeId] = localDerivativeOfFilterOutput[nodeId];
            for (int j = 0; j < cols; j++) {
                gradFilterWeights_ptr[nodeId * cols + j] = localDerivativeOfFilterOutput[nodeId] * attributes[nodeId * cols + j];  // row-major //attributes[j * rows + nodeId];
            }
        }

        torch::Tensor gradWeight = torch::zeros({cols}, torch::kFloat32);
        torch::Tensor gradBias = torch::zeros({1}, torch::kFloat32);

        float* gradWeight_ptr = gradWeight.data_ptr<float>();
        float* gradBias_ptr = gradBias.data_ptr<float>();
        float* gradLoss = gradientOfLoss.data_ptr<float>();

        // Vamos somar os gradientes da loss de cada CC e acumular com o gradiente local.
        std::unique_ptr<float[]> summationGrad_ptr(new float[tree->getNumNodes()]);
        AttributeComputedIncrementally::computerAttribute(
            tree,
            tree->getRootById(),
            [&](NodeId nodeId) -> void { // pre-processing
                summationGrad_ptr[nodeId] = 0;
                for (int p : tree->getCNPsById(nodeId)) {
                    summationGrad_ptr[nodeId] += gradLoss[p];
                }
            },
            [&summationGrad_ptr](NodeId parent, NodeId child) -> void { // merge-processing
                summationGrad_ptr[parent] += summationGrad_ptr[child];
            },
            [&](NodeId nodeId) -> void { // post-processing                
                gradBias_ptr[0] += summationGrad_ptr[nodeId] * gradFilterBias_ptr[nodeId];
                for (int j = 0; j < cols; j++) {
                    gradWeight_ptr[j] += summationGrad_ptr[nodeId] * gradFilterWeights_ptr[nodeId * cols + j];
                }
            }
        );

        return std::make_tuple(gradWeight, gradBias);
    }
    

    /**
     * Gradiente apenas para o parâmetro escalar "threshold".
     *
     * Assumimos que o forward foi:
     *    logits_i = attribute_i - threshold
     *    sigmoid_i = 1 / (1 + exp(-logits_i))
     *    y = filtering(tree, sigmoid)
     *
     * Então:
     *    d(sigmoid_i)/d(threshold) = - sigmoid_i * (1 - sigmoid_i)
     *    d(y)/d(sigmoid_i) = residue_i 
     *    dLoss/dthreshold = sum_nodes [ sum_pixels_in_CC( dLoss/dy[p] ) * residue_i * d(sigmoid_i)/d(threshold) ]
     *
     * Parâmetros:
     *   - treePtr: árvore
     *   - sigmoid: tensor 1D (numNodes) float32
     *   - gradientOfLoss: gradiente da loss no domínio da imagem (H x W), float32
     *
     * Retorno:
     *   - gradThreshold: tensor (1,) float32
     */
    static torch::Tensor gradientsOfThreshold(MorphologicalTreePybindPtr treePtr, torch::Tensor sigmoid, float beta, torch::Tensor gradientOfLoss) {
        MorphologicalTreePybind* tree = treePtr.get();
        float* sigmoid_ptr = sigmoid.data_ptr<float>();
        float* gradLoss = gradientOfLoss.data_ptr<float>();

        // Derivada local d y / d threshold por nó
        std::unique_ptr<float[]> localDerivativeOfFilterOutput(new float[tree->getNumNodes()]);

        // Primeiro, computamos a derivada local:
        // localDerivativeOfFilterOutput[node] = residue(node) * d(sigmoid)/d(threshold)
        // d(sigmoid)/d(threshold) = -beta * sigmoid * (1 - sigmoid)
        for (NodeId nodeId : tree->getNodeIds()) {
            float residue = (tree->getParentById(nodeId) != InvalidNode) ? static_cast<float>(tree->getResidueById(nodeId)) : 0.0f;
            float dSigmoid = -beta * sigmoid_ptr[nodeId] * (1 - sigmoid_ptr[nodeId]);
            localDerivativeOfFilterOutput[nodeId] = residue * dSigmoid;
        }

        torch::Tensor gradThreshold = torch::zeros({1}, torch::kFloat32);
        float* gthr = gradThreshold.data_ptr<float>();
        gthr[0] = 0.0f;

        // Agora, somamos dLoss/dy(p) por nó (somando nos pixels pertencentes à CC do nó)
        std::unique_ptr<float[]> sumGradPerNode(new float[tree->getNumNodes()]);
        AttributeComputedIncrementally::computerAttribute(
            tree,
            tree->getRootById(),
            [&](NodeId nodeId) -> void { // pre-processing
                sumGradPerNode[nodeId] = 0.0f;
                for (int p : tree->getCNPsById(nodeId)) {
                    sumGradPerNode[nodeId] += gradLoss[p];
                }
            },
            [&](NodeId parent, NodeId child) -> void { // merge-processing
                sumGradPerNode[parent] += sumGradPerNode[child];
            },
            [&](NodeId nodeId) -> void { 
                gthr[0] += sumGradPerNode[nodeId] * localDerivativeOfFilterOutput[nodeId];
            }
        );

        return gradThreshold;
    }

    // Gradiente para K parâmetros (um threshold por atributo do grupo).
    // Entradas:
    //   - sigmoids2d: tensor 2D (numNodes, K) float32 com σ_{ik} do forward
    //   - gradientOfLoss: tensor 2D (H, W) float32 com dLoss/dy
    // Saída:
    //   - gradThresholds: tensor 1D (K,) float32 com dLoss/dτ_k
    static torch::Tensor gradientsOfThresholds(MorphologicalTreePybindPtr treePtr, torch::Tensor sigmoids2d, float beta, torch::Tensor gradientOfLoss) {
        MorphologicalTreePybind* tree = treePtr.get();

        //--- checagens básicas ---
        TORCH_CHECK(sigmoids2d.dim() == 2, "sigmoids2d deve ter shape (numNodes, K).");
        TORCH_CHECK(sigmoids2d.dtype() == torch::kFloat32, "sigmoids2d deve ser float32.");
        TORCH_CHECK(gradientOfLoss.dim() == 2, "gradientOfLoss deve ter shape (H, W).");
        TORCH_CHECK(gradientOfLoss.dtype() == torch::kFloat32, "gradientOfLoss deve ser float32.");

        const int64_t numNodes = sigmoids2d.size(0);
        const int64_t K        = sigmoids2d.size(1);
        const float* sigmoids2d_ptr = sigmoids2d.data_ptr<float>();

        // 1) Derivada local por nó e por parâmetro:
        //    localDerivativeOfFilterOutput[i,k] = residue_i * ( - s_i * (1 - s_i) )
        const size_t localSize = static_cast<size_t>(numNodes) * static_cast<size_t>(K);
        std::unique_ptr<float[]> localDerivativeOfFilterOutput(new float[localSize]);
        float* localDerivativeOfFilterOutput_ptr = localDerivativeOfFilterOutput.get();

        for (NodeId nodeId : tree->getNodeIds()) {
            float residue = (tree->getParentById(nodeId) != InvalidNode) ? static_cast<float>(tree->getResidueById(nodeId)) : 0.0f;
            float* dst = localDerivativeOfFilterOutput_ptr + static_cast<int64_t>(nodeId) * K;
            const float* sigmoids_nodeId = sigmoids2d_ptr + static_cast<int64_t>(nodeId) * K;
            for (int64_t k = 0; k < K; ++k) {
                dst[k] = residue * (-beta * sigmoids_nodeId[k] * (1.0f - sigmoids_nodeId[k]) );
            }
        }

        // 2) Somatório de dLoss/dy por CC e agregação final
        float* gradLoss = gradientOfLoss.data_ptr<float>();
        std::unique_ptr<float[]> sumGradPerNode(new float[static_cast<size_t>(numNodes)]);
        auto gradThresholds = torch::zeros({K}, torch::kFloat32);
        float* gthr = gradThresholds.data_ptr<float>();

        AttributeComputedIncrementally::computerAttribute(
            tree,
            tree->getRootById(),
            [&](NodeId nodeId) -> void { // pre-processing
                sumGradPerNode[nodeId] = 0.0f;
                for (int p : tree->getCNPsById(nodeId)) {
                    sumGradPerNode[nodeId] += gradLoss[p];
                }
            },
            [&](NodeId parent, NodeId child) -> void { // merge-processing
                sumGradPerNode[parent] += sumGradPerNode[child];
            },
            [&](NodeId nodeId) -> void { // post-processing
                const float acc = sumGradPerNode[nodeId]; // dL/dy somado nos pixels do nó/CC
                const float* loc = localDerivativeOfFilterOutput_ptr + static_cast<int64_t>(nodeId) * K;
                for (int64_t k = 0; k < K; ++k) {
                    gthr[k] += acc * loc[k];
                }
            }
        );

        return gradThresholds; // (K,)
    }

    

};

} // namespace mtlearn
