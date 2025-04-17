# ✅ Convergence Verification Toolkit — Development Roadmap

This checklist organizes the enhancements planned for the convergence verification program.

---

## 🧱 Phase 1: Foundation Polishing

### 🧮 Standards and Config
- [x] Add `.to_dict()` method to `StandardParameters`
- [x] Add `.to_dict()` and `.to_json()` method to `MeshData`
- [x] Allow loading of user-defined standards via JSON/YAML
- [x] Create a `config.py` to centralize numerical tolerances (e.g., `eps`)

### 📐 Mesh and Dimensionality
- [x] Add optional `dim` field to `MeshData` (default 3)
- [x] Add `units` dictionary to `MeshData` for physical interpretation

### 🚨 Error Handling and Validation
- [x] Add `__repr__()` to exceptions
- [x] Add logging support for `safe_division()` and `safe_log()` clamping events
- [x] Add `verbose=True` flag in `validate_mesh_sequence()` for warnings on non-strict failures

---

## 🚀 Phase 2: Functional Expansion

### 🔁 Generalization of Convergence
- [ ] Allow sliding window analysis with configurable `n-tuple` size
- [ ] Return and label convergence type (asymptotic, oscillatory, uncertain)
- [ ] Support vector-valued or field-based parameters (`List[float]` or tensors)

### 📈 Metrics and Evaluation
- [ ] Output per-mesh refinement ratios in study results
- [ ] Propagate error bounds in Richardson extrapolation
- [ ] Add optional `expected_order` field in standards and test deviation

---

## 📊 Phase 3: User Experience Enhancement

### 📝 Markdown + PDF Reporting
- [ ] Create `report_markdown.py`
- [ ] Add summary block: global GCI stats, pass/fail flags, warnings
- [ ] Use Pandoc or WeasyPrint to export `.md` to `.pdf`

### 📉 Visualization
- [ ] Create `plotting.py` module
  - [ ] Plot GCI vs. mesh level
  - [ ] Plot order vs. triplet index
  - [ ] Plot relative error evolution
- [ ] Embed plots into Markdown/PDF report

---

## 🖥️ Phase 4: Interface & Distribution

### 🛠 Command Line Interface
- [ ] Create `cli.py` using `argparse` or `click`
- [ ] Allow input from `.json` mesh file
- [ ] Export `.txt`, `.md`, `.pdf`, and `.png` outputs

### 🖼 Optional GUI (Stretch Goal)
- [ ] Build basic GUI using Tkinter **OR**
- [ ] Build web GUI using Streamlit
- [ ] Support mesh upload, standard selection, plot display

### 📦 Packaging and Distribution
- [ ] Create installable `convergence_checker/` package
- [ ] Add `setup.py` or `pyproject.toml`
- [ ] Add `__init__.py` to all directories
- [ ] Create `/tests` folder with unit tests using `pytest`

---

## 📚 Final Deliverables

- [ ] `README.md` with usage examples
- [ ] Auto-generated docs via `Sphinx` or `MkDocs`
- [ ] Example dataset folder (e.g., `/examples`)
- [ ] Starter CLI command: `converge-checker --input meshes.json --standard ASME`

---

**Progress bar:**
`[░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0% complete`

Once implemented, this roadmap will elevate the project to a production-grade, fully usable engineering verification suite.
