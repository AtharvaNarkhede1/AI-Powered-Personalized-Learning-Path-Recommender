from __future__ import annotations
import re
from typing import Dict, Iterable, List, Tuple
from app.data.taxonomy_data import SKILLS_DATABASE
_ALIASES = {
    "ml": "Classical Machine Learning (Scikit-Learn)",
    "scikit-learn": "Classical Machine Learning (Scikit-Learn)",
    "sklearn": "Classical Machine Learning (Scikit-Learn)",
    "deep learning": "Deep Learning & PyTorch",
    "pytorch": "Deep Learning & PyTorch",
    "tensorflow": "Deep Learning & PyTorch",
    "keras": "Deep Learning & PyTorch",
    "neural network": "Deep Learning & PyTorch",
    "nlp": "LLMs, Embeddings & RAG Systems",
    "llm": "LLMs, Embeddings & RAG Systems",
    "llms": "LLMs, Embeddings & RAG Systems",
    "rag": "LLMs, Embeddings & RAG Systems",
    "langchain": "LLMs, Embeddings & RAG Systems",
    "transformers": "LLMs, Embeddings & RAG Systems",
    "cv": "Computer Vision & OpenCV",
    "opencv": "Computer Vision & OpenCV",
    "image processing": "Computer Vision & OpenCV",
    "ros": "C++ & ROS 2 Development",
    "ros2": "C++ & ROS 2 Development",
    "k8s": "Docker Containers & Kubernetes",
    "kubernetes": "Docker Containers & Kubernetes",
    "docker": "Docker Containers & Kubernetes",
    "terraform": "Infrastructure as Code (Terraform)",
    "iac": "Infrastructure as Code (Terraform)",
    "ci/cd": "CI/CD Pipeline Automation",
    "cicd": "CI/CD Pipeline Automation",
    "github actions": "CI/CD Pipeline Automation",
    "jenkins": "CI/CD Pipeline Automation",
    "aws": "AWS / Cloud Architecture",
    "azure": "AWS / Cloud Architecture",
    "gcp": "AWS / Cloud Architecture",
    "cloud": "AWS / Cloud Architecture",
    "mlops": "MLOps, Docker & Model Deployment",
    "spark": "Distributed Data Processing (Spark)",
    "pyspark": "Distributed Data Processing (Spark)",
    "etl": "Data Engineering & ETL Pipelines",
    "airflow": "Data Engineering & ETL Pipelines",
    "sql": "SQL & Data Modeling",
    "postgres": "SQL & Data Modeling",
    "mysql": "SQL & Data Modeling",
    "mongodb": "SQL & NoSQL Databases",
    "nosql": "SQL & NoSQL Databases",
    "redis": "SQL & NoSQL Databases",
    "react": "React & Modern Front-End",
    "next.js": "React & Modern Front-End",
    "nextjs": "React & Modern Front-End",
    "typescript": "JavaScript & TypeScript",
    "javascript": "JavaScript & TypeScript",
    "node": "Node.js & Backend Services",
    "node.js": "Node.js & Backend Services",
    "nodejs": "Node.js & Backend Services",
    "express": "Node.js & Backend Services",
    "fastapi": "REST / GraphQL API Design",
    "graphql": "REST / GraphQL API Design",
    "rest api": "REST / GraphQL API Design",
    "linux": "Linux Systems Administration & Shell Scripting",
    "bash": "Linux Systems Administration & Shell Scripting",
    "verilog": "Verilog & SystemVerilog RTL",
    "systemverilog": "Verilog & SystemVerilog RTL",
    "rtl": "Verilog & SystemVerilog RTL",
    "fpga": "FPGA Synthesis (Xilinx / Altera)",
    "uvm": "UVM Verification Frameworks",
    "solidworks": "3D CAD Modeling (SolidWorks/Fusion360)",
    "fusion360": "3D CAD Modeling (SolidWorks/Fusion360)",
    "autocad": "3D CAD Modeling (SolidWorks/Fusion360)",
    "catia": "3D CAD Modeling (SolidWorks/Fusion360)",
    "fea": "Finite Element Analysis (FEA)",
    "ansys": "Finite Element Analysis (FEA)",
    "matlab": "MATLAB & Simulink Model-Based Design",
    "simulink": "MATLAB & Simulink Model-Based Design",
    "freertos": "Real-Time Operating Systems (FreeRTOS)",
    "rtos": "Real-Time Operating Systems (FreeRTOS)",
    "stm32": "Embedded Microcontrollers & Microprocessors",
    "arduino": "Embedded Microcontrollers & Microprocessors",
    "microcontroller": "Embedded Microcontrollers & Microprocessors",
    "embedded c": "Embedded C & Data Structures",
    "arm cortex": "ARM Cortex Architecture & Registers",
    "i2c": "Hardware Communication Protocols (SPI, I2C, CAN, UART)",
    "spi": "Hardware Communication Protocols (SPI, I2C, CAN, UART)",
    "can bus": "Hardware Communication Protocols (SPI, I2C, CAN, UART)",
    "uart": "Hardware Communication Protocols (SPI, I2C, CAN, UART)",
    "mqtt": "IoT Connectivity & Protocols (MQTT, BLE, LoRa)",
    "lora": "IoT Connectivity & Protocols (MQTT, BLE, LoRa)",
    "ble": "IoT Connectivity & Protocols (MQTT, BLE, LoRa)",
    "iot": "IoT Connectivity & Protocols (MQTT, BLE, LoRa)",
    "selenium": "UI Automation (Selenium/Cypress/Playwright)",
    "cypress": "UI Automation (Selenium/Cypress/Playwright)",
    "playwright": "UI Automation (Selenium/Cypress/Playwright)",
    "penetration testing": "Offensive Security & Pen Testing",
    "pentesting": "Offensive Security & Pen Testing",
    "cryptography": "Applied Cryptography",
    "revit": "BIM & Autodesk Revit Structure",
    "staad": "ETABS / STAAD Pro FEA Modeling",
    "etabs": "ETABS / STAAD Pro FEA Modeling",
    "aspen": "Process Simulation (Aspen/DWSIM)",
    "pandas": "Advanced Python & Scientific Computing",
    "numpy": "Advanced Python & Scientific Computing",
    "python": "Advanced Python & Scientific Computing",
    "statistics": "Statistics & Inference",
    "a/b testing": "Experiment Design & A/B Testing",
    "tableau": "Data Visualization & Communication",
    "power bi": "Data Visualization & Communication",
}
_SPLIT = re.compile(r"[,/()]|&| and | with | of ")
_STOP_TERMS = {"design", "systems", "system", "tools", "analysis", "modeling", "development",
               "engineering", "fundamentals", "management", "architecture", "codes", "tech",
               "control", "power", "data", "cloud", "test", "testing", "web", "model", "models",
               "digital", "applied", "core", "advanced", "modern", "protocols", "processing",
               "communication", "dynamics", "inference", "frameworks", "platforms", "services",
               "computing", "scientific", "structural", "materials", "energy", "storage"}

def _terms_for(name: str) -> List[str]:
    low = name.lower()
    parts = [low] + [p.strip() for p in _SPLIT.split(low)]
    return [p for p in parts if len(p) >= 3 and p not in _STOP_TERMS]
def _wb(term: str, text: str) -> bool:
    return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text) is not None
def extract_skills_from_text(text: str, exclude: Iterable[str] = ()) -> List[Dict]:
    text = (text or "").strip()
    if len(text) < 20:
        return []
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    exclude_low = {e.strip().lower() for e in exclude}
    found: Dict[str, Tuple[float, str]] = {}
    for s in SKILLS_DATABASE.values():
        name = s["name"]
        if name.lower() in exclude_low:
            continue
        for i, term in enumerate(_terms_for(name)):
            if _wb(term, low):
                found[name] = (0.95 if i == 0 else 0.85, "resume")
                break
    for alias, canon in _ALIASES.items():
        if canon in found or canon.lower() in exclude_low:
            continue
        if _wb(alias, low):
            found[canon] = (0.8, "resume")
    if len(found) < 6:
        try:
            from app.ml.engine import engine
            snippet = text[:2500]
            for s in SKILLS_DATABASE.values():
                name = s["name"]
                if name in found or name.lower() in exclude_low:
                    continue
                sim = engine.text_sim(name, snippet)
                if sim >= 0.6:
                    found[name] = (round(float(sim), 2), "semantic")
        except Exception:
            pass
    out = [{"name": n, "confidence": c, "source": src} for n, (c, src) in found.items()]
    out.sort(key=lambda x: -x["confidence"])
    return out[:20]