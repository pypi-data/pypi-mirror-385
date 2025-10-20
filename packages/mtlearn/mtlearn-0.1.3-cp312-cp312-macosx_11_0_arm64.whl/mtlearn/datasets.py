# %% setup
import os, glob, time
import numpy as np
import cv2
import torch
from sklearn import model_selection
import abc
import mmcfilters
from torch.utils.data import Dataset

# --------------------------
# 1) AttributeFilterDataset
# --------------------------
class AttributeFilterDataset(torch.utils.data.Dataset, abc.ABC):
    def __init__(self, root, tree_type, attributes: list, thresholds: dict, top_hat: bool = False, numRows: int = None, numCols: int = None):
        super(torch.utils.data.Dataset, self).__init__()

        self.root = root
        exts = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff")
        paths = []
        for e in exts:
            paths.extend(glob.glob(os.path.join(root, e)))
        if not paths:
            raise FileNotFoundError(f"Nenhuma imagem encontrada em {root}")
        paths.sort()
        self.paths = paths
        self.thresholds = thresholds
        self.attributes = attributes
        self.tree_type = tree_type
        self.numRows=numRows
        self.numCols=numCols
        self.top_hat = top_hat

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        path = self.paths[idx]
        img_u8 = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if self.numRows != None and self.numCols != None:
            img_u8 = cv2.resize(img_u8, (self.numCols, self.numRows))
        if img_u8 is None:
            raise RuntimeError(f"Falha ao ler imagem: {path}")
        

        # ----- Filtragem -----
        tree = None
        
        if(self.tree_type == "max-tree"):
            tree = mmcfilters.MorphologicalTree(img_u8, True)
        elif(self.tree_type == "min-tree"):
            tree = mmcfilters.MorphologicalTree(img_u8, False)
        else:
            tree = mmcfilters.MorphologicalTree(img_u8)
        
        attr_idx, attr_values = mmcfilters.Attribute.computeAttributes(tree, self.attributes) # (numNodes, numAttributes)
        criterion = np.ones(attr_values.shape[0], dtype=bool)
        for attr_type in self.attributes:
            name = attr_type.name
            criterion = criterion & (attr_values[:, attr_idx[name]] > self.thresholds[name]) 

        
        filter = mmcfilters.AttributeFilters(tree)
        img_out_u8 = filter.filteringSubtractiveRule(criterion)           # (numRows,numCols) uint8
        if self.top_hat == True:
            if(self.tree_type == "min-tree"):
                img_out_u8 = img_out_u8 - img_u8
            elif(self.tree_type == "max-tree"):
                img_out_u8 = img_u8 - img_out_u8
            else:
                img_out_u8 = np.abs(img_out_u8 - img_u8)

        img_out = torch.from_numpy(img_out_u8).to(torch.float32).unsqueeze(0) # (1,numRows,numCols)
        img_in = torch.from_numpy(img_u8).to(torch.float32).unsqueeze(0) # (1,numRows,numCols)
        
        return img_in, img_out, os.path.basename(path)
            
    
    def train_test_split(self, test_size=0.25, shuffle=True, random_state=42):
        """
        Divide este dataset em (train_dataset, test_dataset), preservando o __getitem__
        e toda a lógica atual. Retorna Subset(self, indices).
    
        Parâmetros
        ----------
        test_size : float|int
            Igual ao do sklearn: fração (0,1] ou número absoluto de amostras no teste.
        shuffle : bool
            Se True, embaralha antes de dividir.
        random_state : int
            Semente para reprodutibilidade.
    
        Retorna
        -------
        (train_subset, test_subset) : (torch.utils.data.Subset, torch.utils.data.Subset)
        """
        indices = np.arange(len(self))
        train_idx, test_idx = model_selection.train_test_split(
            indices,
            test_size=test_size,
            shuffle=shuffle,
            random_state=random_state
            # stratify=None  # adicione aqui se precisar balancear por classe
        )
        # Convertemos para listas para evitar problemas com Subset em algumas versões
        train_subset = torch.utils.data.Subset(self, train_idx.tolist())
        test_subset  = torch.utils.data.Subset(self, test_idx.tolist())
        return train_subset, test_subset




class PairedImageDataset(Dataset):
    """
    Lê pares de imagens no formato:
        01_in.jpg, 01_target.jpg, 02_in.jpg, 02_target.jpg, ...

    Parâmetros
    ----------
    root_dir : str
        Diretório contendo as imagens.
    numRows, numCols : int | None
        Tamanho desejado (aplica apenas se ambos definidos).
    grayscale_in : bool
        Se True, INPUT é carregado em escala de cinza (1 canal).
    grayscale_target : bool
        Se True, TARGET é carregado em escala de cinza (1 canal).
    invert_in : bool
        Se True, aplica negativo (255 - img) **antes** da normalização na entrada.
    invert_target : bool
        Se True, aplica negativo (255 - img) **antes** da normalização no alvo.
    extensions : tuple[str, ...]
        Extensões suportadas.
    dtype : torch.dtype
        Tipo dos tensores de saída (padrão float32).
    scale_0_1 : bool
        Se True, normaliza para [0, 1]; caso contrário, mantém [0,255] (float).
    prefix_in, prefix_target, suffix_in, suffix_target : str
        Regras de nome para localizar pares.
    """

    def __init__(
        self,
        root_dir: str,
        numRows: int | None = None,
        numCols: int | None = None,
        *,
        grayscale_in: bool = True,
        grayscale_target: bool = True,
        invert_in: bool = False,
        invert_target: bool = False,
        extensions: tuple = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"),
        dtype: torch.dtype = torch.float32,
        scale_0_1: bool = True,
        prefix_in: str = "",
        prefix_target: str = "",
        suffix_in: str = "_in",
        suffix_target: str = "_target",
    ):
        self.root_dir = root_dir
        self.numRows = numRows
        self.numCols = numCols
        self.grayscale_in = bool(grayscale_in)
        self.grayscale_target = bool(grayscale_target)
        self.invert_in = bool(invert_in)
        self.invert_target = bool(invert_target)
        self.extensions = tuple(e.lower() for e in extensions)
        self.dtype = dtype
        self.scale_0_1 = bool(scale_0_1)
        self.prefix_in = prefix_in
        self.prefix_target = prefix_target
        self.suffix_in = suffix_in
        self.suffix_target = suffix_target

        if (self.numRows is None) ^ (self.numCols is None):
            print("[PairedImageDataset] Aviso: numRows e numCols devem ser ambos None ou ambos definidos. "
                  "Resize será ignorado porque apenas um foi fornecido.")
            self.numRows = None
            self.numCols = None

        self.pairs = self._scan_pairs()
        if not self.pairs:
            raise RuntimeError(
                f"Nenhum par *_in / *_target encontrado em {root_dir} "
                f"com extensões {self.extensions}."
            )

    # --------- API Dataset ---------
    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx: int):
        in_path, tgt_path = self.pairs[idx]

        # Leitura com modo de cor independente
        img_in = self._read_image(in_path, self.grayscale_in)
        img_tg = self._read_image(tgt_path, self.grayscale_target)

        # Invertemos apenas conforme os flags correspondentes
        if self.invert_in:
            img_in = self._invert(img_in)
        if self.invert_target:
            img_tg = self._invert(img_tg)

        # Redimensionamento (se definido)
        if self.numRows is not None and self.numCols is not None:
            img_in = cv2.resize(img_in, (self.numCols, self.numRows), interpolation=cv2.INTER_AREA)
            img_tg = cv2.resize(img_tg, (self.numCols, self.numRows), interpolation=cv2.INTER_NEAREST)

        # Conversão para tensor (mantendo flags separados)
        tin = self._to_tensor(img_in, self.grayscale_in)
        ttg = self._to_tensor(img_tg, self.grayscale_target)
        return tin, ttg, os.path.basename(in_path)

    # --------- Helpers ---------
    def _scan_pairs(self):
        pairs = []
        suffix_in_len = len(self.suffix_in)
        for ext in self.extensions:
            pattern = os.path.join(self.root_dir, f"{self.prefix_in}*{self.suffix_in}{ext}")
            for fpath in glob.glob(pattern):
                base = os.path.basename(fpath)
                if not base.startswith(self.prefix_in) or not base.endswith(self.suffix_in + ext):
                    continue
                stem = base[len(self.prefix_in):-suffix_in_len - len(ext)]
                target_path = None
                for ext_t in self.extensions:
                    candidate = f"{self.prefix_target}{stem}{self.suffix_target}{ext_t}"
                    cand = os.path.join(self.root_dir, candidate)
                    if os.path.exists(cand):
                        target_path = cand
                        break
                if target_path is not None:
                    pairs.append((fpath, target_path))

        pairs.sort(key=lambda p: p[0])
        return pairs

    def _read_image(self, path: str, grayscale_flag: bool) -> np.ndarray:
        """Lê com cv2 e retorna ndarray (H,W) se grayscale_flag, ou (H,W,3) RGB se color."""
        if grayscale_flag:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise RuntimeError(f"Falha ao ler (grayscale) {path}")
            return img
        else:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                raise RuntimeError(f"Falha ao ler (color) {path}")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img

    @staticmethod
    def _invert(img: np.ndarray) -> np.ndarray:
        if img.dtype != np.uint8:
            img_u8 = np.clip(img, 0, 255).astype(np.uint8)
            return 255 - img_u8
        return 255 - img

    def _to_tensor(self, img: np.ndarray, grayscale_flag: bool) -> torch.Tensor:
        """Converte ndarray para tensor (C,H,W): (1,H,W) se grayscale, senão (3,H,W)."""
        if grayscale_flag:
            tensor = torch.from_numpy(img).unsqueeze(0)  # (1,H,W)
        else:
            tensor = torch.from_numpy(img).permute(2, 0, 1)  # (3,H,W)

        tensor = tensor.to(self.dtype)
        if self.scale_0_1:
            tensor = tensor / 255.0
        return tensor

    def train_test_split(self, test_size=0.25, shuffle=True, random_state=42):
        indices = np.arange(len(self))
        train_idx, test_idx = model_selection.train_test_split(
            indices, test_size=test_size, shuffle=shuffle, random_state=random_state
        )
        return (
            torch.utils.data.Subset(self, train_idx.tolist()),
            torch.utils.data.Subset(self, test_idx.tolist()),
        )