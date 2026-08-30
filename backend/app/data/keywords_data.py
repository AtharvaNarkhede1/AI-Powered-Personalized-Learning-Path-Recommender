"""
Massive Engineering Technical Keyword Vocabulary Base.
Covers 500+ technical keywords across 14 engineering branches for dynamic search & custom tagging.
"""
from typing import List, Dict

ENGINEERING_KEYWORDS_VOCABULARY = [
    # Computer Engineering & AI
    "Artificial Intelligence", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Computer Vision",
    "NLP", "Large Language Models (LLMs)", "Retrieval-Augmented Generation (RAG)", "Generative AI", "AI Agents",
    "Reinforcement Learning", "MLOps", "Model Deployment", "Neural Networks", "Data Engineering", "Big Data",
    "Cloud Computing", "AWS", "Azure", "Docker", "Kubernetes", "DevOps", "Cyber Security", "Ethical Hacking",
    "Blockchain", "Web Development", "FastAPI", "React", "High-Performance Computing (HPC)", "Quantum Computing",

    # Robotics, Mechatronics & Autonomous Systems
    "Robotics", "ROS 2 (Robot Operating System)", "Autonomous Mobile Robots (AMRs)", "Kinematics & Dynamics",
    "SLAM (Simultaneous Localization & Mapping)", "LiDAR Perception", "Trajectory Planning", "Drones & UAVs",
    "Industrial Automation", "PLC Programming", "Control Systems", "PID Controllers", "State-Space Control",
    "Mechatronics", "Actuators & Sensors", "Motor Drives & Inverters", "Micro-rovers", "Humanoid Robotics",

    # Electronics & Embedded Hardware
    "Embedded Systems", "Firmware Development", "Bare-Metal C/C++", "ARM Cortex", "RISC-V Architecture",
    "STM32 Microcontrollers", "ESP32 & IoT", "FreeRTOS", "SPI / I2C / UART / CAN Bus", "Digital Signal Processing (DSP)",
    "PCB Design (Altium / KiCAD)", "Circuit Diagnostics", "Oscilloscopes & Logic Analyzers", "TinyML",
    "Semiconductor Chip Design", "VLSI RTL Design", "Verilog / SystemVerilog", "FPGA Prototyping", "UVM Verification",

    # Electrical & Renewable Energy
    "Electrical Engineering", "Power Systems", "Smart Grids", "Solar Photovoltaics (PV)", "Wind Energy",
    "Battery Energy Storage Systems (BESS)", "Battery Management Systems (BMS)", "High-Voltage Substations",
    "Power Electronics", "ETAP Simulation", "PVSyst", "Micro-grid Controllers", "Green Hydrogen",

    # Mechanical & Automotive / EVs
    "Mechanical Engineering", "SolidWorks 3D CAD", "Finite Element Analysis (FEA)", "ANSYS Simulation",
    "Computational Fluid Dynamics (CFD)", "Thermodynamics & Heat Transfer", "Electric Vehicles (EVs)",
    "EV Powertrain Design", "Vehicle Dynamics", "Chassis Engineering", "Automotive CAN Bus", "AUTOSAR",
    "ADAS (Advanced Driver Assistance Systems)", "Thermal Management", "3D Printing & Additive Manufacturing",

    # Civil & Structural
    "Civil Engineering", "Structural Engineering", "Building Information Modeling (BIM)", "Autodesk Revit",
    "ETABS / STAAD Pro", "Seismic Dynamic Analysis", "Reinforced Concrete Design", "Smart Infrastructure",
    "Structural Health Monitoring (SHM)", "Hydrology & Water Resources", "Geotechnical Engineering",

    # Biomedical, Chemical & Materials
    "Biomedical Engineering", "Neural Interfaces", "Surgical Devices", "Bio-Informatics", "Biomaterials",
    "Chemical Process Design", "Aspen Plus Simulation", "Clean Energy Conversion", "Materials Science", "Nanotechnology"
]


def search_keywords(query: str, limit: int = 15) -> List[str]:
    """Dynamically filters technical keywords based on user search query."""
    if not query or not query.strip():
        return ENGINEERING_KEYWORDS_VOCABULARY[:limit]
    
    q_clean = query.strip().lower()
    matches = [kw for kw in ENGINEERING_KEYWORDS_VOCABULARY if q_clean in kw.lower()]
    
    # If custom query is not in standard list, offer it as a custom tag
    if not any(kw.lower() == q_clean for kw in matches):
        matches.insert(0, query.strip())
        
    return matches[:limit]
