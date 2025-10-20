#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <torch/extension.h>

#include "mtlearn/core.hpp"
#include "ConnectedFilterByJacobian.hpp"
#include "ConnectedFilterByMorphologicalTree.hpp"
#include "InfoTreePybind.hpp"

namespace py = pybind11;

void init_ComputerDerivative(py::module& m){

    py::class_<mtlearn::ConnectedFilterByJacobian>(m, "ConnectedFilterByJacobian")
        .def_static(
            "gradients",
            &mtlearn::ConnectedFilterByJacobian::gradients,
            py::arg("jacobian"),
            py::arg("residues"),
            py::arg("attributes"),
            py::arg("sigmoid"),
            py::arg("grad_output"),
            "Aplica a jacobiana esparsa para projetar gradientes de nós para pixels.")
        .def_static(
            "filtering",
            &mtlearn::ConnectedFilterByJacobian::filtering,
            py::arg("pixel_to_node"),
            py::arg("residues"),
            py::arg("sigmoid"),
            "Reconstrói a saída por pixel sem depender da árvore C++ completa.")
        .def_static(
            "compute_gradients_efficient",
            &mtlearn::ConnectedFilterByJacobian::computeGradientsEfficient,
            py::arg("pixel_to_node"),
            py::arg("residues"),
            py::arg("sigmoid"),
            py::arg("attributes"),
            py::arg("grad_output"),
            "Gradientes otimizados usando apenas vetores auxiliares no PyTorch.");

    py::class_<mtlearn::ConnectedFilterByMorphologicalTree>(m, "ConnectedFilterByMorphologicalTree")
        .def_static(
            "filtering",
            &mtlearn::ConnectedFilterByMorphologicalTree::filtering,
            py::arg("tree"),
            py::arg("sigmoid"),
            "Reconstrói a imagem filtrada.")
        // --- gradientes p/ pesos e bias (assinatura antiga, 4 args) ---
        .def_static(
            "gradients",
            &mtlearn::ConnectedFilterByMorphologicalTree::gradients,
            py::arg("tree"),
            py::arg("attributes"),
            py::arg("sigmoid"),
            py::arg("beta_f"),
            py::arg("grad_output"),
            "Calcula gradientes de weight e bias a partir da estrutura da árvore."
        )
        // --- gradiente p/ thresholds
        .def_static(
            "gradientsOfThresholds",
            &mtlearn::ConnectedFilterByMorphologicalTree::gradientsOfThresholds,
            py::arg("tree"),
            py::arg("sigmoid"),
            py::arg("beta"),
            py::arg("grad_output"),
            "Calcula gradiente dos thresholds (logits = attributes - thresholds)."
        )
        // --- gradiente p/ 1 threshold
        .def_static(
            "gradientsOfThreshold",
            &mtlearn::ConnectedFilterByMorphologicalTree::gradientsOfThreshold,
            py::arg("tree"),
            py::arg("sigmoid"),
            py::arg("beta"),
            py::arg("grad_output"),
            "Calcula gradiente apenas de um threshold (logits = attribute - threshold)."
        );
}

void init_InfoTree(py::module& m)
{

    py::class_<mtlearn::InfoTreePybind>(m, "InfoTree")
        .def_static(
            "get_residues",
            &mtlearn::InfoTreePybind::getResidues,
            py::arg("tree"),
            "Obtém os resíduos de todos os nós da árvore como um tensor."
        )
        .def_static(
            "get_jacobian",
            &mtlearn::InfoTreePybind::getJacobian,
            py::arg("tree"),
            "Obtém a matriz jacobiana da árvore como um tensor."
        );
}

void init_tests(py::module& m)
{
    py::class_<mtlearn::TreeStats>(m, "TreeStats")
        .def(py::init<>())
        .def_readwrite("num_nodes", &mtlearn::TreeStats::numNodes)
        .def("describe", [](const mtlearn::TreeStats& stats) {
            return mtlearn::describeTree(stats);
        });

    m.def(
        "make_tree_stats",
        [](int numNodes) {
            return mtlearn::makeTreeStats(numNodes);
        },
        py::arg("num_nodes"),
        "Create a simple TreeStats instance using a node count.");

    m.def(
        "make_tree_tensor",
        [](int numNodes) {
            auto stats = mtlearn::makeTreeStats(numNodes);
            auto tensor = torch::arange(numNodes, torch::dtype(torch::kFloat32));
            return py::make_tuple(stats, tensor);
        },
        py::arg("num_nodes"),
        "Return TreeStats and a torch tensor with a simple range.");


}

PYBIND11_MODULE(_mtlearn, m)
{
    m.doc() = "Python bindings for MTLearn built on top of mmcfilters";
    m.attr("WITH_TORCH") = true;
    init_ComputerDerivative(m);
    init_InfoTree(m);
    init_tests(m);
}
