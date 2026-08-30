from typing import List, Dict
ENGINEERING_KEYWORDS_VOCABULARY = [
    "Artificial Intelligence", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Computer Vision",
    "NLP", "Large Language Models (LLMs)", "Retrieval-Augmented Generation (RAG)", "Generative AI", "AI Agents",
    "Reinforcement Learning", "MLOps", "Model Deployment", "Neural Networks", "Data Engineering", "Big Data",
    "Cloud Computing", "AWS", "Azure", "Docker", "Kubernetes", "DevOps", "Cyber Security", "Ethical Hacking",
    "Blockchain", "Web Development", "FastAPI", "React", "High-Performance Computing (HPC)", "Quantum Computing",
    "Robotics", "ROS 2 (Robot Operating System)", "Autonomous Mobile Robots (AMRs)", "Kinematics & Dynamics",
    "SLAM (Simultaneous Localization & Mapping)", "LiDAR Perception", "Trajectory Planning", "Drones & UAVs",
    "Industrial Automation", "PLC Programming", "Control Systems", "PID Controllers", "State-Space Control",
    "Mechatronics", "Actuators & Sensors", "Motor Drives & Inverters", "Micro-rovers", "Humanoid Robotics",
    "Embedded Systems", "Firmware Development", "Bare-Metal C/C++", "ARM Cortex", "RISC-V Architecture",
    "STM32 Microcontrollers", "ESP32 & IoT", "FreeRTOS", "SPI / I2C / UART / CAN Bus", "Digital Signal Processing (DSP)",
    "PCB Design (Altium / KiCAD)", "Circuit Diagnostics", "Oscilloscopes & Logic Analyzers", "TinyML",
    "Semiconductor Chip Design", "VLSI RTL Design", "Verilog / SystemVerilog", "FPGA Prototyping", "UVM Verification",
    "Electrical Engineering", "Power Systems", "Smart Grids", "Solar Photovoltaics (PV)", "Wind Energy",
    "Battery Energy Storage Systems (BESS)", "Battery Management Systems (BMS)", "High-Voltage Substations",
    "Power Electronics", "ETAP Simulation", "PVSyst", "Micro-grid Controllers", "Green Hydrogen",
    "Mechanical Engineering", "SolidWorks 3D CAD", "Finite Element Analysis (FEA)", "ANSYS Simulation",
    "Computational Fluid Dynamics (CFD)", "Thermodynamics & Heat Transfer", "Electric Vehicles (EVs)",
    "EV Powertrain Design", "Vehicle Dynamics", "Chassis Engineering", "Automotive CAN Bus", "AUTOSAR",
    "ADAS (Advanced Driver Assistance Systems)", "Thermal Management", "3D Printing & Additive Manufacturing",
    "Civil Engineering", "Structural Engineering", "Building Information Modeling (BIM)", "Autodesk Revit",
    "ETABS / STAAD Pro", "Seismic Dynamic Analysis", "Reinforced Concrete Design", "Smart Infrastructure",
    "Structural Health Monitoring (SHM)", "Hydrology & Water Resources", "Geotechnical Engineering",
    "Biomedical Engineering", "Neural Interfaces", "Surgical Devices", "Bio-Informatics", "Biomaterials",
    "Chemical Process Design", "Aspen Plus Simulation", "Clean Energy Conversion", "Materials Science", "Nanotechnology"
]
def search_keywords(query: str, limit: int = 15) -> List[str]:
    """Dynamically filters technical keywords based on user search query."""
    if not query or not query.strip():
        return ENGINEERING_KEYWORDS_VOCABULARY[:limit]    
    q_clean = query.strip().lower()
    matches = [kw for kw in ENGINEERING_KEYWORDS_VOCABULARY if q_clean in kw.lower()]
    if not any(kw.lower() == q_clean for kw in matches):
        matches.insert(0, query.strip())      
    return matches[:limit]