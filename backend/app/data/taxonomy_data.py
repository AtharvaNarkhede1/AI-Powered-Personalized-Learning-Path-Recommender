"""
Expanded Multi-Branch Engineering Knowledge Taxonomy & Resource Dataset.
Includes:
- 14 Engineering Branches
- 45+ Deeply Modeled Careers
- 60+ Modeled Skills & DAG Prerequisite Dependency Graph
- Top YouTube Channels & Free/Paid Recommended Courses per Domain
- Diagnostic Assessments & Personalised 'What NOT to Do' Rules
"""

ENGINEERING_BRANCHES = [
    "Computer Engineering / IT",
    "Electronics & Communication Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Aerospace Engineering",
    "Biomedical Engineering",
    "Instrumentation & Control",
    "Industrial / Production Engineering",
    "Automobile Engineering",
    "Robotics / Mechatronics",
    "Environmental Engineering",
    "Materials / Metallurgy"
]

CAREERS_DATABASE = [
    {
        "career_id": "robotics_eng",
        "title": "Robotics & Automation Engineer",
        "category": "Robotics / Embedded / AI",
        "branch_primary": "Robotics / Mechatronics",
        "branches_compatible": ["Mechanical Engineering", "Electronics & Communication Engineering", "Computer Engineering / IT", "Electrical Engineering"],
        "description": "Designs, builds, and programs autonomous robotic systems, mechatronic actuators, computer vision inspection units, and industrial automation controls.",
        "avg_salary_range": "$85,000 - $145,000 / yr",
        "job_demand": "Very High",
        "key_responsibilities": [
            "Program industrial arm kinematic controllers and autonomous mobile robots (AMRs)",
            "Develop ROS 2 (Robot Operating System) nodes for navigation and obstacle avoidance",
            "Integrate sensory hardware (LiDAR, cameras, IMUs, torque sensors)",
            "Design embedded motor control firmware (C++, microcontrollers, CAN bus)"
        ],
        "required_skills": [
            {"skill_id": "math_kinematics", "name": "Linear Algebra & Kinematics", "level": 0.85, "critical": True},
            {"skill_id": "cpp_ros", "name": "C++ & ROS 2 Development", "level": 0.9, "critical": True},
            {"skill_id": "embedded_sys", "name": "Embedded Microcontrollers & Microprocessors", "level": 0.8, "critical": True},
            {"skill_id": "computer_vision", "name": "Computer Vision & OpenCV", "level": 0.75, "critical": False},
            {"skill_id": "control_theory", "name": "Control Systems (PID, State-Space)", "level": 0.8, "critical": True},
            {"skill_id": "cad_modeling", "name": "3D CAD Modeling (SolidWorks/Fusion360)", "level": 0.7, "critical": False}
        ],
        "day_in_the_life": "Split between 3D mechanical simulations, writing low-level C++ sensor drivers, debugging ROS 2 motion planning code on physical robot hardware, and calibrating vision system cameras.",
        "hard_realities": [
            "Hardware bugs can break physical hardware—testing requires caution and simulation safety boundaries.",
            "Requires equal comfort with mechanical physics, electronics hardware debugging, and high-performance algorithms."
        ],
        "common_misconceptions": [
            "Misconception: Robotics is just building humanoid robots.",
            "Reality: Most robotics roles focus on warehouse AMRs, surgical instruments, automated factory lines, and specialized drones."
        ],
        "future_evolution": [
            "Integration of Vision-Language-Action (VLA) foundation models into physical humanoid and quadrupeds.",
            "Rise of real-time GPU-accelerated simulation platforms like NVIDIA Isaac Sim."
        ],
        "emerging_specializations": ["Autonomous Mobile Robot (AMR) Navigation", "Robotic Perception Specialist", "Surgical Robotics Engineer"],
        "what_not_to_do": [
            "DON'T jump straight into ROS 2 navigation stacks before mastering basic C++ pointers, object-oriented concepts, and Linux terminal command line.",
            "DON'T rely solely on computer simulations; build at least one real physical micro-rover or arm with an ESP32 or Raspberry Pi.",
            "DON'T skip classical control theory (PID, state-space) thinking AI/ML solves all motor control problems—it does not."
        ]
    },
    {
        "career_id": "aiml_eng",
        "title": "AI & Machine Learning Engineer",
        "category": "Artificial Intelligence / Software",
        "branch_primary": "Computer Engineering / IT",
        "branches_compatible": ["Electronics & Communication Engineering", "Electrical Engineering", "Mathematics", "Robotics / Mechatronics"],
        "description": "Builds, fine-tunes, and deploys predictive machine learning models, deep neural networks, computer vision systems, and Large Language Model (LLM) applications.",
        "avg_salary_range": "$100,000 - $175,000 / yr",
        "job_demand": "Very High",
        "key_responsibilities": [
            "Train and validate deep learning models using PyTorch / TensorFlow",
            "Build RAG (Retrieval-Augmented Generation) architectures and fine-tune LLMs",
            "Develop scalable inference APIs using FastAPI and ONNX runtime",
            "Optimize vector databases, embeddings, and prompt engineering pipelines"
        ],
        "required_skills": [
            {"skill_id": "python_core", "name": "Advanced Python & Scientific Computing", "level": 0.9, "critical": True},
            {"skill_id": "math_stats", "name": "Linear Algebra, Calculus & Probability", "level": 0.85, "critical": True},
            {"skill_id": "machine_learning", "name": "Classical Machine Learning (Scikit-Learn)", "level": 0.85, "critical": True},
            {"skill_id": "deep_learning", "name": "Deep Learning & PyTorch", "level": 0.85, "critical": True},
            {"skill_id": "llm_rag", "name": "LLMs, Embeddings & RAG Systems", "level": 0.8, "critical": False},
            {"skill_id": "mlops", "name": "MLOps, Docker & Model Deployment", "level": 0.75, "critical": True}
        ],
        "day_in_the_life": "Analyzing data distributions, writing PyTorch custom training loops, evaluating model accuracy and latency, building FastAPI microservices, and debugging GPU memory constraints.",
        "hard_realities": [
            "80% of real ML engineering is data cleaning, feature engineering, and pipeline maintenance, not tweaking model hyper-parameters.",
            "Deploying models to production requires software engineering excellence (Docker, APIs, latency optimization) beyond Jupyter Notebooks."
        ],
        "common_misconceptions": [
            "Misconception: Prompt engineering alone makes you an AI Engineer.",
            "Reality: Real AI engineering requires deep statistical knowledge, vector mathematical understanding, PyTorch architecture mastery, and systems engineering."
        ],
        "future_evolution": [
            "Transition from static LLMs to autonomous multi-agent systems.",
            "Edge AI deployment on low-power neural processing units (NPUs)."
        ],
        "emerging_specializations": ["LLM / GenAI Application Architect", "Edge AI & Quantization Specialist", "MLOps & AI Infrastructure Engineer"],
        "what_not_to_do": [
            "DON'T jump directly into advanced LLM fine-tuning or Transformer architectures without mastering supervised learning fundamentals (Linear/Logistic Regression, Decision Trees, Gradient Boosting).",
            "DON'T keep all your work in Jupyter Notebooks—convert models into production FastAPI code with unit tests and Docker containers.",
            "DON'T ignore linear algebra and gradient descent math; without it, debugging model convergence failure is impossible."
        ]
    },
    {
        "career_id": "embedded_eng",
        "title": "Embedded Systems & Firmware Engineer",
        "category": "Hardware / Systems",
        "branch_primary": "Electronics & Communication Engineering",
        "branches_compatible": ["Electrical Engineering", "Computer Engineering / IT", "Instrumentation & Control", "Robotics / Mechatronics"],
        "description": "Develops real-time firmware, micro-controller code (ARM Cortex, RISC-V), hardware drivers, and IoT communication protocols for smart devices and industrial hardware.",
        "avg_salary_range": "$80,000 - $135,000 / yr",
        "job_demand": "High",
        "key_responsibilities": [
            "Write bare-metal C/C++ and RTOS (FreeRTOS) drivers for STM32 / ESP32 microcontrollers",
            "Implement hardware communication protocols (SPI, I2C, UART, CAN, BLE)",
            "Debug physical hardware using oscilloscopes, logic analyzers, and JTAG debuggers",
            "Optimize power consumption, memory footprint, and real-time responsiveness"
        ],
        "required_skills": [
            {"skill_id": "c_embedded", "name": "Embedded C & Data Structures", "level": 0.9, "critical": True},
            {"skill_id": "microcontrollers", "name": "ARM Cortex Architecture & Registers", "level": 0.85, "critical": True},
            {"skill_id": "rtos", "name": "Real-Time Operating Systems (FreeRTOS)", "level": 0.8, "critical": True},
            {"skill_id": "comm_protocols", "name": "Hardware Protocols (SPI, I2C, CAN, UART)", "level": 0.85, "critical": True},
            {"skill_id": "digital_electronics", "name": "Digital Electronics & Circuit Diagnostics", "level": 0.75, "critical": False}
        ],
        "day_in_the_life": "Writing C code to configure microcontroller registers, hooking up logic analyzers to observe SPI bus clock lines, debugging interrupt service routines, and optimizing battery microamps.",
        "hard_realities": [
            "Debugging firmware often requires reading 1,000-page silicon vendor datasheets and inspecting memory registers byte-by-byte.",
            "Compiler error messages are replaced by hardware hard-faults and silent system resets."
        ],
        "common_misconceptions": [
            "Misconception: Embedded engineering is just writing Arduino sketches.",
            "Reality: Industry firmware development uses C/C++, direct register manipulation, RTOS task synchronization, memory constraints, and strict safety standards."
        ],
        "future_evolution": [
            "TinyML: Running micro-neural networks directly on microcontrollers.",
            "Widespread adoption of Rust for memory-safe embedded systems."
        ],
        "emerging_specializations": ["TinyML Firmware Engineer", "Automotive CAN / AUTOSAR Developer", "Medical Device Firmware Specialist"],
        "what_not_to_do": [
            "DON'T limit your learning to high-level Arduino libraries; learn registers, memory pointers, bitwise operations, and memory maps.",
            "DON'T ignore hardware schematics—an embedded software engineer must be able to read circuit diagrams and datasheet pinouts.",
            "DON'T neglect RTOS mutexes and race conditions when writing multi-threaded firmware."
        ]
    },
    {
        "career_id": "automotive_eng",
        "title": "Autonomous & EV Automotive Engineer",
        "category": "Automotive / Mobility",
        "branch_primary": "Automobile Engineering",
        "branches_compatible": ["Mechanical Engineering", "Electrical Engineering", "Electronics & Communication Engineering", "Robotics / Mechatronics"],
        "description": "Engineers electric vehicle powertrain systems, battery management systems (BMS), vehicle dynamics controllers, and autonomous driving sensors.",
        "avg_salary_range": "$82,000 - $140,000 / yr",
        "job_demand": "High",
        "key_responsibilities": [
            "Design EV battery pack cooling, cell balancing, and high-voltage distribution",
            "Develop CAN bus automotive diagnostic nodes and AUTOSAR software components",
            "Simulate vehicle dynamics, braking systems, and aerodynamics using MATLAB/Simulink",
            "Perform real-world road and track testing of ADAS (Advanced Driver Assistance Systems)"
        ],
        "required_skills": [
            {"skill_id": "ev_powertrain", "name": "EV Powertrain & Battery Management", "level": 0.85, "critical": True},
            {"skill_id": "matlab_simulink", "name": "MATLAB & Simulink Model-Based Design", "level": 0.85, "critical": True},
            {"skill_id": "vehicle_dynamics", "name": "Vehicle Dynamics & Chassis Engineering", "level": 0.8, "critical": True},
            {"skill_id": "comm_protocols", "name": "CAN Bus & Automotive Ethernet", "level": 0.8, "critical": True},
            {"skill_id": "cad_modeling", "name": "3D CAD & Mechanical Simulation", "level": 0.75, "critical": False}
        ],
        "day_in_the_life": "Modeling thermal runaway in battery packs using Simulink, analyzing CAN logs captured during test track runs, tuning regenerative braking control algorithms, and verifying ISO 26262 functional safety compliance.",
        "hard_realities": [
            "Automotive safety compliance (ISO 26262) means extensive documentation and rigorous testing before code touches a car.",
            "High voltage (400V - 800V EV systems) requires strict electrical safety protocols."
        ],
        "common_misconceptions": [
            "Misconception: Automotive engineering is purely mechanical engine design.",
            "Reality: Modern EVs are software-defined vehicles on wheels—software, electronics, and battery chemistry now dominate."
        ],
        "future_evolution": [
            "800V ultra-fast charging architecture standardization.",
            "Full Drive-by-Wire steering and software-defined vehicle platforms."
        ],
        "emerging_specializations": ["BMS Firmware Specialist", "ADAS Sensor Fusion Engineer", "EV Thermal Management Designer"],
        "what_not_to_do": [
            "DON'T focus exclusively on internal combustion engines (ICE)—the industry shifts overwhelmingly toward EVs and hybrid architectures.",
            "DON'T skip MATLAB/Simulink statechart modeling if aiming for OEM automotive tier-1 suppliers.",
            "DON'T ignore automotive communication standards like CAN bus and LIN bus."
        ]
    },
    {
        "career_id": "cloud_devops_eng",
        "title": "Cloud & DevOps Solutions Architect",
        "category": "Cloud / Infrastructure",
        "branch_primary": "Computer Engineering / IT",
        "branches_compatible": ["Electronics & Communication Engineering", "Electrical Engineering", "Industrial / Production Engineering"],
        "description": "Architects cloud infrastructure (AWS/Azure/GCP), builds CI/CD automated deployment pipelines, manages Kubernetes clusters, and ensures zero-downtime reliability.",
        "avg_salary_range": "$95,000 - $165,000 / yr",
        "job_demand": "Very High",
        "key_responsibilities": [
            "Architect resilient cloud infrastructure using Terraform (Infrastructure as Code)",
            "Build automated CI/CD deployment pipelines (GitHub Actions, GitLab CI)",
            "Orchestrate containerized applications using Docker and Kubernetes (EKS/GKE)",
            "Monitor system performance, logging, and security posture using Prometheus/Grafana"
        ],
        "required_skills": [
            {"skill_id": "linux_sys", "name": "Linux Systems Administration & Shell Scripting", "level": 0.9, "critical": True},
            {"skill_id": "aws_cloud", "name": "AWS / Cloud Architecture", "level": 0.85, "critical": True},
            {"skill_id": "docker_k8s", "name": "Docker Containers & Kubernetes", "level": 0.85, "critical": True},
            {"skill_id": "terraform", "name": "Infrastructure as Code (Terraform)", "level": 0.8, "critical": True},
            {"skill_id": "cicd_pipelines", "name": "CI/CD Pipeline Automation", "level": 0.8, "critical": True}
        ],
        "day_in_the_life": "Writing Terraform manifests, managing Kubernetes pod scaling alerts, setting up IAM security roles, optimizing AWS cloud bills, and automating application releases.",
        "hard_realities": [
            "On-call rotations mean dealing with production outages and infrastructure degradation in real-time.",
            "Cloud security mistakes can expose sensitive user databases or cause massive unbudgeted cloud bills."
        ],
        "common_misconceptions": [
            "Misconception: DevOps is just clicking buttons in AWS console.",
            "Reality: Professional cloud architecture is 100% written as code (Terraform), version-controlled, automated, and mathematically monitored."
        ],
        "future_evolution": [
            "GitOps workflow automation with ArgoCD.",
            "AI-assisted cloud cost optimization and automated security remediation."
        ],
        "emerging_specializations": ["Site Reliability Engineer (SRE)", "Cloud Security Architect", "Platform Engineer"],
        "what_not_to_do": [
            "DON'T create infrastructure manually via Web AWS Console; learn Infrastructure as Code (Terraform / CloudFormation) from day one.",
            "DON'T ignore Linux command line and networking fundamentals (IP subnets, DNS, TCP/IP, SSH).",
            "DON'T deploy Kubernetes clusters without understanding basic Docker container containerization first."
        ]
    },
    {
        "career_id": "vlsi_chip_eng",
        "title": "VLSI & Semiconductor Chip Designer",
        "category": "Semiconductors / Hardware",
        "branch_primary": "Electronics & Communication Engineering",
        "branches_compatible": ["Electrical Engineering", "Computer Engineering / IT", "Materials / Metallurgy"],
        "description": "Designs integrated circuits (ICs), microprocessors, and SOCs using Verilog/SystemVerilog hardware description languages, logic synthesis, and physical layout verification.",
        "avg_salary_range": "$90,000 - $160,000 / yr",
        "job_demand": "High",
        "key_responsibilities": [
            "Write RTL hardware code in Verilog / SystemVerilog for digital logic blocks",
            "Perform functional verification and UVM (Universal Verification Methodology) testbenches",
            "Synthesize logic using EDA tools (Cadence / Synopsys) and optimize Static Timing Analysis (STA)",
            "Design ASIC and FPGA prototype boards"
        ],
        "required_skills": [
            {"skill_id": "verilog_sv", "name": "Verilog & SystemVerilog RTL", "level": 0.9, "critical": True},
            {"skill_id": "digital_design", "name": "Digital Logic & Computer Architecture", "level": 0.9, "critical": True},
            {"skill_id": "fpga_prototyping", "name": "FPGA Synthesis (Xilinx / Altera)", "level": 0.8, "critical": True},
            {"skill_id": "sta_timing", "name": "Static Timing Analysis & EDA Tools", "level": 0.75, "critical": False},
            {"skill_id": "uvm_verification", "name": "UVM Verification Frameworks", "level": 0.75, "critical": False}
        ],
        "day_in_the_life": "Writing Verilog state machines, running cycle-accurate waveform simulations in ModelSim, fixing timing violation paths in chip layouts, and validating FPGA dev boards.",
        "hard_realities": [
            "Silicon tape-out is irreversible and costs millions—a single logic flaw requires complete re-spining of the chip wafer.",
            "EDA software licensing is highly commercialized; open-source silicon tools (Verilator/OpenLane) are growing but proprietary tools dominate."
        ],
        "common_misconceptions": [
            "Misconception: Writing Verilog is just like writing software C code.",
            "Reality: Hardware Description Languages describe parallel physical transistors executing concurrently, not sequential software commands."
        ],
        "future_evolution": [
            "RISC-V open instruction set architecture takeover.",
            "3D Chiplet packaging and AI accelerator silicon."
        ],
        "emerging_specializations": ["RTL Design Engineer", "Design Verification (DV) Specialist", "Physical Design & Layout Engineer"],
        "what_not_to_do": [
            "DON'T confuse software programming loops with hardware synthesizable logic—think in registers, clocks, and flip-flops.",
            "DON'T skip learning FPGA prototyping boards before applying for VLSI internships.",
            "DON'T ignore digital logic timing constraints and clock domain crossing (CDC) hazards."
        ]
    },
    {
        "career_id": "renewable_energy_eng",
        "title": "Renewable Energy & Smart Grid Engineer",
        "category": "Energy / Sustainability",
        "branch_primary": "Electrical Engineering",
        "branches_compatible": ["Chemical Engineering", "Mechanical Engineering", "Environmental Engineering", "Civil Engineering"],
        "description": "Designs solar PV plants, wind farm micro-grids, battery energy storage systems (BESS), and smart power distribution grids.",
        "avg_salary_range": "$78,000 - $130,000 / yr",
        "job_demand": "High",
        "key_responsibilities": [
            "Design high-voltage electrical substations and solar grid-tied inverters",
            "Model renewable generation profiles using PVSyst and Homer Pro",
            "Integrate Battery Energy Storage Systems (BESS) for grid frequency regulation",
            "Analyze power quality, transient stability, and load flow using ETAP"
        ],
        "required_skills": [
            {"skill_id": "power_systems", "name": "Power Systems & Load Flow Analysis", "level": 0.85, "critical": True},
            {"skill_id": "solar_wind_design", "name": "Solar PV & Wind Farm Engineering", "level": 0.85, "critical": True},
            {"skill_id": "bess_storage", "name": "Grid Energy Storage & Battery Tech", "level": 0.8, "critical": True},
            {"skill_id": "etap_pvsyst", "name": "ETAP & PVSyst Simulation Tools", "level": 0.8, "critical": True},
            {"skill_id": "high_voltage", "name": "Substations & High Voltage Protection", "level": 0.75, "critical": False}
        ],
        "day_in_the_life": "Simulating grid stability during solar irradiance drops, sizing utility battery storage systems, performing short-circuit studies in ETAP, and reviewing electrical schematics.",
        "hard_realities": [
            "Utility grid connections require navigating complex regulatory utility permits and strict grid code compliance.",
            "Intermittent solar/wind energy requires deep understanding of power electronics and grid stability."
        ],
        "common_misconceptions": [
            "Misconception: Renewable energy is just putting solar panels on rooftops.",
            "Reality: Utility-scale renewable engineering involves gigawatt power transmission, high-voltage transformers, power factor correction, and grid-tied inverters."
        ],
        "future_evolution": [
            "Green hydrogen electrolyzer integration.",
            "AI-powered predictive smart grid demand response management."
        ],
        "emerging_specializations": ["Utility BESS Engineer", "Smart Grid Integration Specialist", "Green Hydrogen Energy Architect"],
        "what_not_to_do": [
            "DON'T skip fundamental AC power system theory (phasors, 3-phase power, reactive power, transformer impedance).",
            "DON'T assume solar modeling is simple calculation—learn industry simulation tools like PVSyst and ETAP.",
            "DON'T ignore energy storage (batteries/hydro) which is critical for solving renewable intermittency."
        ]
    },
    {
        "career_id": "structural_eng",
        "title": "Structural & Smart Infrastructure Engineer",
        "category": "Civil / Structural",
        "branch_primary": "Civil Engineering",
        "branches_compatible": ["Mechanical Engineering", "Materials / Metallurgy", "Environmental Engineering"],
        "description": "Designs seismic-resistant high-rise structures, bridges, smart infrastructure sensor monitoring systems, and sustainable concrete/steel frameworks.",
        "avg_salary_range": "$75,000 - $125,000 / yr",
        "job_demand": "Medium High",
        "key_responsibilities": [
            "Perform structural finite element analysis (FEA) using ETABS, SAP2000, and STAAD Pro",
            "Design reinforced concrete (RC) and structural steel frames according to building codes",
            "Implement Building Information Modeling (BIM) workflows in Revit Structure",
            "Conduct structural health monitoring (SHM) using IoT strain and vibration sensors"
        ],
        "required_skills": [
            {"skill_id": "solid_mechanics", "name": "Mechanics of Materials & Structural Analysis", "level": 0.9, "critical": True},
            {"skill_id": "etabs_staad", "name": "ETABS / STAAD Pro FEA Modeling", "level": 0.85, "critical": True},
            {"skill_id": "bim_revit", "name": "BIM & Autodesk Revit Structure", "level": 0.8, "critical": True},
            {"skill_id": "steel_concrete_design", "name": "Reinforced Concrete & Steel Design Codes", "level": 0.85, "critical": True},
            {"skill_id": "seismic_eng", "name": "Seismic & Wind Dynamic Analysis", "level": 0.75, "critical": False}
        ],
        "day_in_the_life": "Building 3D structural models in ETABS, running lateral wind and earthquake dynamic load simulations, auditing rebar reinforcement calculations, and inspecting job sites.",
        "hard_realities": [
            "Structural safety carries public liability; all calculations must adhere strictly to building codes (IS / ACI / Eurocodes).",
            "Transitioning from academic formulas to complex 3D BIM coordination requires mastering BIM software platforms."
        ],
        "common_misconceptions": [
            "Misconception: Civil engineering is just managing manual laborers on construction sites.",
            "Reality: Modern structural engineering relies heavily on advanced mathematical FEA simulations, computational parametric design, and smart IoT sensor health monitoring."
        ],
        "future_evolution": [
            "Generative structural optimization reducing steel/concrete carbon footprints.",
            "3D concrete printing of residential and bridge infrastructure."
        ],
        "emerging_specializations": ["Seismic Retrofit Specialist", "Smart Infrastructure Sensor Architect", "Parametric BIM Structural Designer"],
        "what_not_to_do": [
            "DON'T rely blindly on software output (ETABS/STAAD) without doing hand verification of bending moments and shear forces.",
            "DON'T skip 3D BIM tool mastery (Revit Structure)—hand drawings are obsolete in commercial projects.",
            "DON'T ignore seismic dynamic load response principles if practicing in earthquake-prone zones."
        ]
    },
    {
        "career_id": "edge_ai_eng",
        "title": "Edge AI & Micro-NPU Hardware Specialist",
        "category": "AI / Hardware / Embedded",
        "branch_primary": "Electronics & Communication Engineering",
        "branches_compatible": ["Computer Engineering / IT", "Robotics / Mechatronics", "Electrical Engineering"],
        "description": "Optimizes and deploys deep neural networks onto constrained low-power microcontrollers, Raspberry Pi, NVIDIA Jetson, and specialized Neural Processing Units (NPUs).",
        "avg_salary_range": "$95,000 - $160,000 / yr",
        "job_demand": "Very High",
        "key_responsibilities": [
            "Quantize and prune PyTorch / TensorFlow models for 8-bit / 4-bit edge inference",
            "Convert neural networks to TensorRT, ONNX, and TFLite Micro runtimes",
            "Optimize memory buffer bandwidth on ARM Cortex-M and RISC-V NPUs",
            "Deploy low-latency computer vision vision-at-the-edge hardware"
        ],
        "required_skills": [
            {"skill_id": "python_core", "name": "Advanced Python & Scientific Computing", "level": 0.85, "critical": True},
            {"skill_id": "c_embedded", "name": "Embedded C & Data Structures", "level": 0.9, "critical": True},
            {"skill_id": "deep_learning", "name": "Deep Learning & PyTorch", "level": 0.85, "critical": True},
            {"skill_id": "edge_ai", "name": "Edge AI Quantization & TensorRT", "level": 0.9, "critical": True}
        ],
        "day_in_the_life": "Benchmarking inference millisecond latency on NVIDIA Jetson Orin boards, executing post-training quantization, and profiling NPU SRAM utilization.",
        "hard_realities": [
            "Model accuracy often drops during 8-bit quantization—requires careful fine-tuning and calibration dataset selection.",
            "Requires combined expertise in both deep learning neural network math and hardware memory constraints."
        ],
        "common_misconceptions": [
            "Misconception: Edge AI is just running Python scripts on a laptop.",
            "Reality: Real Edge AI optimizes C++ runtimes on low-power microchips with strict milliwatt power budgets."
        ],
        "future_evolution": [
            "Ultra-low power Neuromorphic Spiking Neural Network hardware.",
            "On-device privacy-preserving local LLMs running on phones and laptops."
        ],
        "emerging_specializations": ["TinyML Engineer", "NVIDIA Jetson Perception Specialist", "NPU Compiler Optimization Engineer"],
        "what_not_to_do": [
            "DON'T deploy un-quantized 32-bit floating point models to microcontrollers—always quantize to INT8.",
            "DON'T ignore C++ runtime bindings when deploying PyTorch models."
        ]
    },
]


def _career(career_id, title, category, branch_primary, compatible, description, salary, demand,
            responsibilities, required_skills, day, realities, misconceptions, evolution,
            specializations, avoid):
    """Compact constructor so the broadened catalog stays readable."""
    return {
        "career_id": career_id, "title": title, "category": category,
        "branch_primary": branch_primary, "branches_compatible": compatible,
        "description": description, "avg_salary_range": salary, "job_demand": demand,
        "key_responsibilities": responsibilities, "required_skills": required_skills,
        "day_in_the_life": day, "hard_realities": realities,
        "common_misconceptions": misconceptions, "future_evolution": evolution,
        "emerging_specializations": specializations, "what_not_to_do": avoid,
    }


CAREERS_DATABASE += [
    _career(
        "data_eng", "Data Engineer", "Data / Backend", "Computer Engineering / IT",
        ["Electronics & Communication Engineering", "Electrical Engineering", "Industrial / Production Engineering"],
        "Builds and operates the pipelines, warehouses, and streaming systems that move and shape data for analytics and ML.",
        "$90,000 - $155,000 / yr", "Very High",
        ["Design batch and streaming ETL/ELT pipelines", "Model and tune data warehouses and lakehouses",
         "Orchestrate workflows with Airflow / dbt", "Guarantee data quality, lineage, and SLAs"],
        [{"skill_id": "python_core", "name": "Advanced Python & Scientific Computing", "level": 0.8, "critical": True},
         {"skill_id": "sql", "name": "SQL & Data Modeling", "level": 0.9, "critical": True},
         {"skill_id": "data_pipelines", "name": "Data Engineering & ETL Pipelines", "level": 0.85, "critical": True},
         {"skill_id": "spark_bigdata", "name": "Distributed Data Processing (Spark)", "level": 0.8, "critical": True},
         {"skill_id": "docker_k8s", "name": "Docker Containers & Kubernetes", "level": 0.7, "critical": False},
         {"skill_id": "aws_cloud", "name": "AWS / Cloud Architecture", "level": 0.7, "critical": False}],
        "Writing dbt models, debugging a late-arriving Kafka partition, backfilling a warehouse table, and reviewing pipeline SLAs.",
        ["Most incidents are data quality issues, not code bugs.", "On-call means fixing pipelines at 3am when a source schema changes."],
        ["Misconception: Data engineering is just writing SQL.", "Reality: It is distributed systems, orchestration, and reliability engineering for data."],
        ["Shift from batch to streaming-first architectures.", "Lakehouse formats (Iceberg, Delta) replacing classic warehouses."],
        ["Streaming Data Engineer", "Analytics Engineer (dbt)", "DataOps / Platform Engineer"],
        ["DON'T skip SQL fundamentals and indexing—no framework rescues a bad data model.",
         "DON'T build pipelines with no tests, monitoring, or idempotency."]),
    _career(
        "fullstack_web_eng", "Full-Stack Web Developer", "Software / Web", "Computer Engineering / IT",
        ["Electronics & Communication Engineering", "Electrical Engineering"],
        "Builds complete web applications end to end: responsive front-ends, REST/GraphQL APIs, databases, and deployment.",
        "$75,000 - $140,000 / yr", "Very High",
        ["Build React/Next.js front-ends with accessible, responsive UI", "Design and version REST/GraphQL APIs",
         "Model relational and document databases", "Ship with CI/CD and observability"],
        [{"skill_id": "javascript", "name": "JavaScript & TypeScript", "level": 0.9, "critical": True},
         {"skill_id": "react_frontend", "name": "React & Modern Front-End", "level": 0.85, "critical": True},
         {"skill_id": "nodejs_backend", "name": "Node.js & Backend Services", "level": 0.8, "critical": True},
         {"skill_id": "rest_apis", "name": "REST / GraphQL API Design", "level": 0.8, "critical": True},
         {"skill_id": "databases", "name": "SQL & NoSQL Databases", "level": 0.75, "critical": True},
         {"skill_id": "cicd_pipelines", "name": "CI/CD Pipeline Automation", "level": 0.6, "critical": False}],
        "Building a React feature, wiring an API endpoint, fixing an N+1 query, and reviewing a teammate's pull request.",
        ["The framework churn is real; fundamentals (HTTP, the DOM, SQL) outlast them.", "'Full-stack' still means being genuinely good at both halves."],
        ["Misconception: Knowing React makes you a full-stack developer.", "Reality: You also need API design, data modeling, auth, and deployment."],
        ["Edge rendering and server components.", "Type-safe end-to-end stacks (tRPC, GraphQL codegen)."],
        ["Front-End Platform Engineer", "API / Backend Specialist", "DX / Tooling Engineer"],
        ["DON'T learn a framework before understanding JavaScript, HTTP, and the browser.",
         "DON'T ignore accessibility, security (XSS/CSRF), and testing."]),
    _career(
        "cybersec_eng", "Cybersecurity Engineer", "Security", "Computer Engineering / IT",
        ["Electronics & Communication Engineering", "Electrical Engineering", "Instrumentation & Control"],
        "Defends systems and networks: threat modeling, secure architecture, detection engineering, and incident response.",
        "$95,000 - $165,000 / yr", "Very High",
        ["Threat-model applications and infrastructure", "Build detections and run incident response",
         "Harden cloud and network configurations", "Run vulnerability management and pen tests"],
        [{"skill_id": "linux_sys", "name": "Linux Systems Administration & Shell Scripting", "level": 0.85, "critical": True},
         {"skill_id": "network_security", "name": "Networking & Network Security", "level": 0.9, "critical": True},
         {"skill_id": "cryptography", "name": "Applied Cryptography", "level": 0.75, "critical": True},
         {"skill_id": "pentesting", "name": "Offensive Security & Pen Testing", "level": 0.8, "critical": True},
         {"skill_id": "python_core", "name": "Python for Security Automation", "level": 0.7, "critical": False},
         {"skill_id": "aws_cloud", "name": "Cloud Security", "level": 0.7, "critical": False}],
        "Reviewing an architecture for trust boundaries, tuning SIEM rules, triaging an alert, and writing a remediation report.",
        ["Defense is asymmetric—you must be right every time.", "Compliance paperwork is a real and large part of the job."],
        ["Misconception: Security is all offensive hacking.", "Reality: Most roles are defensive engineering, detection, and response."],
        ["Identity-first / zero-trust architectures.", "Detection-as-code and automated response."],
        ["Detection Engineer", "Cloud Security Architect", "Application Security Engineer"],
        ["DON'T jump to exploit tools before mastering networking, Linux, and how systems actually work.",
         "DON'T practice offensive techniques on systems you are not authorized to test."]),
    _career(
        "mech_design_eng", "Mechanical Design Engineer", "Mechanical / Product", "Mechanical Engineering",
        ["Automobile Engineering", "Aerospace Engineering", "Robotics / Mechatronics", "Industrial / Production Engineering"],
        "Designs mechanical parts and assemblies: CAD modeling, tolerancing, material selection, FEA validation, and design for manufacturing.",
        "$70,000 - $115,000 / yr", "High",
        ["Create parametric CAD models and drawings", "Apply GD&T and tolerance stack-up analysis",
         "Run structural and thermal FEA", "Design for manufacturing and assembly (DFM/DFA)"],
        [{"skill_id": "cad_modeling", "name": "3D CAD Modeling (SolidWorks/Fusion360)", "level": 0.9, "critical": True},
         {"skill_id": "gd_t", "name": "GD&T & Tolerance Analysis", "level": 0.8, "critical": True},
         {"skill_id": "fea_analysis", "name": "Finite Element Analysis (FEA)", "level": 0.8, "critical": True},
         {"skill_id": "solid_mechanics", "name": "Mechanics of Materials & Structural Analysis", "level": 0.85, "critical": True},
         {"skill_id": "thermodynamics", "name": "Thermodynamics & Heat Transfer", "level": 0.7, "critical": False}],
        "Iterating a bracket design in CAD, running an FEA load case, updating a tolerance stack, and releasing drawings to manufacturing.",
        ["A design that can't be manufactured economically is worthless.", "Hand calculations must back up every simulation result."],
        ["Misconception: CAD skill is the whole job.", "Reality: Materials, manufacturing, tolerancing, and validation matter more."],
        ["Generative / topology-optimized design.", "Simulation-driven design in the CAD tool itself."],
        ["FEA / Simulation Engineer", "DFM Specialist", "Product Design Engineer"],
        ["DON'T trust FEA output without mesh convergence and hand-calc sanity checks.",
         "DON'T design parts without knowing how they will be manufactured."]),
    _career(
        "power_systems_eng", "Power Systems Engineer", "Energy / Electrical", "Electrical Engineering",
        ["Electronics & Communication Engineering", "Environmental Engineering", "Mechanical Engineering"],
        "Plans, protects, and operates electrical power systems: generation, transmission, distribution, and grid protection.",
        "$80,000 - $135,000 / yr", "High",
        ["Run load flow, short-circuit, and stability studies", "Design protection and relay coordination schemes",
         "Model power electronics and grid interconnection", "Support substation and distribution design"],
        [{"skill_id": "power_systems", "name": "Power Systems & Load Flow Analysis", "level": 0.9, "critical": True},
         {"skill_id": "protective_relaying", "name": "Protection & Relay Coordination", "level": 0.85, "critical": True},
         {"skill_id": "power_electronics", "name": "Power Electronics & Converters", "level": 0.8, "critical": True},
         {"skill_id": "etap_pvsyst", "name": "ETAP / Power System Simulation", "level": 0.8, "critical": True},
         {"skill_id": "matlab_simulink", "name": "MATLAB & Simulink Model-Based Design", "level": 0.7, "critical": False}],
        "Building an ETAP model, coordinating relay settings, reviewing an interconnection study, and checking arc-flash calculations.",
        ["Mistakes risk equipment damage and human safety.", "Regulatory and utility standards drive most design decisions."],
        ["Misconception: Renewables made classic power engineering obsolete.", "Reality: Grid integration made phasors, protection, and stability more important."],
        ["Inverter-dominated grids and grid-forming control.", "Wide-area monitoring and DER management."],
        ["Protection Engineer", "Grid Integration Engineer", "Substation Design Engineer"],
        ["DON'T skip per-unit system, symmetrical components, and phasor analysis.",
         "DON'T rely on software defaults for protection settings."]),
    _career(
        "biomedical_device_eng", "Biomedical Device Engineer", "Medical / Hardware", "Biomedical Engineering",
        ["Electronics & Communication Engineering", "Mechanical Engineering", "Instrumentation & Control"],
        "Develops medical devices and instrumentation under regulatory constraints: sensing, signal processing, safety, and verification.",
        "$78,000 - $125,000 / yr", "High",
        ["Design biosignal acquisition and instrumentation", "Implement signal processing for physiological data",
         "Run design controls, risk analysis, and V&V", "Support regulatory submissions (FDA/CE)"],
        [{"skill_id": "biomaterials", "name": "Biomedical Instrumentation & Sensors", "level": 0.85, "critical": True},
         {"skill_id": "signal_processing", "name": "Biosignal & Digital Signal Processing", "level": 0.85, "critical": True},
         {"skill_id": "c_embedded", "name": "Embedded C & Data Structures", "level": 0.75, "critical": True},
         {"skill_id": "medical_imaging", "name": "Medical Imaging Fundamentals", "level": 0.6, "critical": False},
         {"skill_id": "python_core", "name": "Python for Data Analysis", "level": 0.6, "critical": False}],
        "Filtering an ECG signal, bench-testing a sensor board, updating a risk file, and writing a verification protocol.",
        ["Regulatory documentation can exceed the engineering effort.", "A field failure can harm a patient—verification is non-negotiable."],
        ["Misconception: It's just electronics with a medical label.", "Reality: Design controls, biocompatibility, and human factors dominate."],
        ["Wearable and continuous monitoring devices.", "AI-assisted diagnostics as regulated software."],
        ["Medical Device Firmware Engineer", "Verification & Validation Engineer", "Clinical Systems Engineer"],
        ["DON'T treat documentation and traceability as an afterthought.",
         "DON'T ignore electrical safety and isolation requirements for patient-connected devices."]),
    _career(
        "aerospace_systems_eng", "Aerospace Systems Engineer", "Aerospace", "Aerospace Engineering",
        ["Mechanical Engineering", "Electrical Engineering", "Robotics / Mechatronics"],
        "Designs and integrates aircraft and spacecraft systems: aerodynamics, propulsion, structures, GNC, and system-level trade studies.",
        "$85,000 - $140,000 / yr", "Medium High",
        ["Perform aerodynamic and performance analysis", "Model flight dynamics and control", "Run structural and thermal analysis",
         "Own system requirements and integration"],
        [{"skill_id": "aerodynamics", "name": "Aerodynamics & Fluid Mechanics", "level": 0.85, "critical": True},
         {"skill_id": "flight_dynamics", "name": "Flight Dynamics & Control", "level": 0.85, "critical": True},
         {"skill_id": "propulsion", "name": "Propulsion Systems", "level": 0.8, "critical": True},
         {"skill_id": "matlab_simulink", "name": "MATLAB & Simulink Model-Based Design", "level": 0.8, "critical": True},
         {"skill_id": "solid_mechanics", "name": "Structural Analysis", "level": 0.75, "critical": False}],
        "Running a performance sweep in MATLAB, reviewing a CFD result, updating a requirements trace, and sitting in an integration review.",
        ["Certification and safety margins slow everything down for good reason.", "System-level thinking matters more than any single discipline."],
        ["Misconception: It's all rockets.", "Reality: Most work is aircraft systems, avionics, UAVs, and satellites."],
        ["Electric and hybrid propulsion.", "Reusable launch and small-satellite constellations."],
        ["GNC Engineer", "Propulsion Analyst", "Systems Integration Engineer"],
        ["DON'T skip fundamental fluid mechanics and dynamics for CFD tools.",
         "DON'T optimize one subsystem without checking system-level impact."]),
    _career(
        "chemical_process_eng", "Chemical Process Engineer", "Process / Chemical", "Chemical Engineering",
        ["Environmental Engineering", "Materials / Metallurgy", "Industrial / Production Engineering"],
        "Designs and optimizes chemical processes and plants: mass/energy balances, reactor and separation design, simulation, and process control.",
        "$75,000 - $120,000 / yr", "Medium High",
        ["Build steady-state and dynamic process simulations", "Design reactors, distillation, and heat integration",
         "Develop process control and safety systems (HAZOP)", "Optimize yield, energy, and emissions"],
        [{"skill_id": "process_simulation", "name": "Process Simulation (Aspen/DWSIM)", "level": 0.85, "critical": True},
         {"skill_id": "reaction_engineering", "name": "Reaction Engineering & Kinetics", "level": 0.85, "critical": True},
         {"skill_id": "thermodynamics", "name": "Chemical Thermodynamics", "level": 0.8, "critical": True},
         {"skill_id": "process_control", "name": "Process Dynamics & Control", "level": 0.8, "critical": True},
         {"skill_id": "python_core", "name": "Python for Process Data", "level": 0.55, "critical": False}],
        "Converging an Aspen flowsheet, sizing a heat exchanger, reviewing a P&ID, and running a HAZOP node.",
        ["Process safety incidents can be catastrophic.", "Scale-up from lab to plant breaks naive assumptions."],
        ["Misconception: It's just chemistry.", "Reality: It's transport phenomena, thermodynamics, control, and economics."],
        ["Electrification and green hydrogen processes.", "Digital twins for plant optimization."],
        ["Process Simulation Engineer", "Process Safety Engineer", "Process Control Engineer"],
        ["DON'T trust a simulation you can't back with a hand mass/energy balance.",
         "DON'T design a process without considering safety and controllability."]),
    _career(
        "iot_eng", "IoT Systems Engineer", "IoT / Connected Hardware", "Electronics & Communication Engineering",
        ["Computer Engineering / IT", "Electrical Engineering", "Instrumentation & Control", "Robotics / Mechatronics"],
        "Builds connected device systems end to end: sensor firmware, wireless connectivity, cloud ingestion, and device management.",
        "$80,000 - $130,000 / yr", "High",
        ["Write sensor firmware and low-power connectivity stacks", "Implement MQTT/CoAP and device provisioning",
         "Build cloud ingestion and device fleet management", "Secure the device-to-cloud pipeline"],
        [{"skill_id": "c_embedded", "name": "Embedded C & Data Structures", "level": 0.85, "critical": True},
         {"skill_id": "iot_protocols", "name": "IoT Connectivity & Protocols (MQTT, BLE, LoRa)", "level": 0.85, "critical": True},
         {"skill_id": "comm_protocols", "name": "Hardware Protocols (SPI, I2C, UART)", "level": 0.8, "critical": True},
         {"skill_id": "cloud_iot", "name": "Cloud IoT Platforms & Ingestion", "level": 0.75, "critical": True},
         {"skill_id": "python_core", "name": "Python for Backend & Data", "level": 0.6, "critical": False}],
        "Debugging a dropped BLE connection, sizing a message payload, wiring an MQTT topic to a database, and checking battery life.",
        ["Field devices are hard to update—get it right before shipping.", "Security is often bolted on too late."],
        ["Misconception: IoT is just connecting a sensor to WiFi.", "Reality: Power budgets, intermittent networks, provisioning, and fleet ops dominate."],
        ["Matter/Thread for interoperable smart devices.", "Edge preprocessing to cut cloud costs."],
        ["Connectivity Firmware Engineer", "IoT Cloud/Backend Engineer", "Device Security Engineer"],
        ["DON'T ignore power consumption and offline behavior.",
         "DON'T ship devices without secure provisioning and OTA updates."]),
    _career(
        "qa_automation_eng", "QA / Test Automation Engineer", "Software / Quality", "Computer Engineering / IT",
        ["Electronics & Communication Engineering", "Industrial / Production Engineering", "Electrical Engineering"],
        "Designs test strategy and builds automated test suites and CI gates that keep software releases fast and safe.",
        "$70,000 - $120,000 / yr", "High",
        ["Design test plans and coverage strategy", "Build UI, API, and integration test automation",
         "Wire tests into CI/CD as release gates", "Track flakiness, coverage, and defect trends"],
        [{"skill_id": "python_core", "name": "Python or JavaScript for Test Code", "level": 0.8, "critical": True},
         {"skill_id": "test_automation", "name": "Test Strategy & Automation Frameworks", "level": 0.9, "critical": True},
         {"skill_id": "selenium_cypress", "name": "UI Automation (Selenium/Cypress/Playwright)", "level": 0.8, "critical": True},
         {"skill_id": "rest_apis", "name": "API Testing", "level": 0.75, "critical": True},
         {"skill_id": "ci_testing", "name": "Continuous Integration for Test Suites", "level": 0.7, "critical": False}],
        "Writing a Playwright spec, triaging a flaky test, adding an API contract test, and reviewing a coverage report.",
        ["Automating the wrong things wastes more time than manual testing.", "Flaky suites destroy team trust fast."],
        ["Misconception: QA is just clicking through the app.", "Reality: It's test design, automation engineering, and release risk management."],
        ["AI-assisted test generation and self-healing locators.", "Shift-left contract and property-based testing."],
        ["SDET (Software Engineer in Test)", "Performance Test Engineer", "Release / CI Engineer"],
        ["DON'T automate everything through the UI—prefer API and unit levels.",
         "DON'T let a flaky suite stay green-ish; fix or quarantine tests."]),
    _career(
        "data_scientist", "Data Scientist", "Data / AI", "Computer Engineering / IT",
        ["Electrical Engineering", "Electronics & Communication Engineering", "Industrial / Production Engineering", "Mechanical Engineering"],
        "Turns data into decisions: framing problems, statistical analysis, modeling, experimentation, and communicating results.",
        "$90,000 - $160,000 / yr", "Very High",
        ["Frame business questions as data problems", "Run exploratory analysis and statistical testing",
         "Build and validate predictive models", "Design experiments and communicate findings"],
        [{"skill_id": "python_core", "name": "Advanced Python & Scientific Computing", "level": 0.85, "critical": True},
         {"skill_id": "statistics", "name": "Statistics & Inference", "level": 0.9, "critical": True},
         {"skill_id": "machine_learning", "name": "Classical Machine Learning (Scikit-Learn)", "level": 0.85, "critical": True},
         {"skill_id": "sql", "name": "SQL & Data Wrangling", "level": 0.8, "critical": True},
         {"skill_id": "data_viz", "name": "Data Visualization & Communication", "level": 0.7, "critical": True},
         {"skill_id": "experiment_design", "name": "Experiment Design & A/B Testing", "level": 0.7, "critical": False}],
        "Pulling data with SQL, running an EDA notebook, fitting a model, checking an A/B test for significance, and presenting to stakeholders.",
        ["Most of the job is data cleaning and stakeholder alignment.", "A model nobody trusts or uses has zero value."],
        ["Misconception: Data science is deep learning.", "Reality: It's mostly statistics, SQL, clean analysis, and communication."],
        ["Causal inference and decision science.", "Productionizing analysis with lightweight ML platforms."],
        ["ML-leaning Data Scientist", "Product Data Scientist", "Decision / Causal Scientist"],
        ["DON'T reach for a neural network before a baseline and solid EDA.",
         "DON'T report a result without checking assumptions and significance."]),
]

SKILLS_DATABASE = {
    "python_core": {
        "id": "python_core",
        "name": "Advanced Python & Scientific Computing",
        "category": "Software",
        "prerequisites": [],
        "resources": [
            {
                "id": "yt_py_01",
                "title": "Python for Beginners & Data Science Full Course (YouTube)",
                "type": "video",
                "provider": "freeCodeCamp.org (YouTube)",
                "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
                "duration_hours": 6,
                "difficulty": "beginner",
                "skills_covered": ["python_core"],
                "rating": 4.95,
                "is_free": True
            },
            {
                "id": "yt_py_02",
                "title": "Core Python Programming & OOP Concepts",
                "type": "video",
                "provider": "Corey Schafer (YouTube)",
                "url": "https://www.youtube.com/user/schafer5",
                "duration_hours": 10,
                "difficulty": "intermediate",
                "skills_covered": ["python_core"],
                "rating": 4.98,
                "is_free": True
            }
        ]
    },
    "math_stats": {
        "id": "math_stats",
        "name": "Linear Algebra, Calculus & Probability",
        "category": "Mathematics",
        "prerequisites": [],
        "resources": [
            {
                "id": "yt_math_01",
                "title": "Essence of Linear Algebra (YouTube Playlist)",
                "type": "video",
                "provider": "3Blue1Brown (YouTube)",
                "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
                "duration_hours": 5,
                "difficulty": "beginner",
                "skills_covered": ["math_stats"],
                "rating": 4.99,
                "is_free": True
            },
            {
                "id": "yt_math_02",
                "title": "StatQuest: Statistics & Machine Learning Fundamentals",
                "type": "video",
                "provider": "StatQuest with Josh Starmer (YouTube)",
                "url": "https://www.youtube.com/c/joshstarmer",
                "duration_hours": 12,
                "difficulty": "beginner",
                "skills_covered": ["math_stats"],
                "rating": 4.97,
                "is_free": True
            }
        ]
    },
    "machine_learning": {
        "id": "machine_learning",
        "name": "Classical Machine Learning (Scikit-Learn)",
        "category": "AI/ML",
        "prerequisites": ["python_core", "math_stats"],
        "resources": [
            {
                "id": "yt_ml_01",
                "title": "Machine Learning Course for Beginners (YouTube)",
                "type": "video",
                "provider": "freeCodeCamp / Andrew Ng (YouTube)",
                "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
                "duration_hours": 18,
                "difficulty": "beginner",
                "skills_covered": ["machine_learning"],
                "rating": 4.95,
                "is_free": True
            },
            {
                "id": "yt_ml_02",
                "title": "Machine Learning & Scikit-Learn Tutorials",
                "type": "video",
                "provider": "Sentdex (YouTube)",
                "url": "https://www.youtube.com/user/sentdex",
                "duration_hours": 15,
                "difficulty": "intermediate",
                "skills_covered": ["machine_learning"],
                "rating": 4.9,
                "is_free": True
            }
        ]
    },
    "deep_learning": {
        "id": "deep_learning",
        "name": "Deep Learning & PyTorch",
        "category": "AI/ML",
        "prerequisites": ["machine_learning"],
        "resources": [
            {
                "id": "yt_dl_01",
                "title": "Neural Networks: Zero to Hero (PyTorch Masterclass)",
                "type": "video",
                "provider": "Andrej Karpathy (YouTube)",
                "url": "https://www.youtube.com/playlist?list=SLaMtzZJwPpyBns_1G7u6g6d0hFz3F99b",
                "duration_hours": 15,
                "difficulty": "intermediate",
                "skills_covered": ["deep_learning"],
                "rating": 5.0,
                "is_free": True
            },
            {
                "id": "yt_dl_02",
                "title": "PyTorch for Deep Learning & Computer Vision Full Course",
                "type": "video",
                "provider": "freeCodeCamp / Daniel Bourke (YouTube)",
                "url": "https://www.youtube.com/watch?v=Z_ikDlimN6A",
                "duration_hours": 25,
                "difficulty": "intermediate",
                "skills_covered": ["deep_learning"],
                "rating": 4.96,
                "is_free": True
            }
        ]
    },
    "llm_rag": {
        "id": "llm_rag",
        "name": "LLMs, Embeddings & RAG Systems",
        "category": "AI/ML",
        "prerequisites": ["deep_learning"],
        "resources": [
            {
                "id": "yt_rag_01",
                "title": "LangChain & LlamaIndex RAG Masterclass (YouTube)",
                "type": "video",
                "provider": "Alejandro AO - Software & AI (YouTube)",
                "url": "https://www.youtube.com/c/AlejandroAO",
                "duration_hours": 8,
                "difficulty": "intermediate",
                "skills_covered": ["llm_rag"],
                "rating": 4.92,
                "is_free": True
            }
        ]
    },
    "cpp_ros": {
        "id": "cpp_ros",
        "name": "C++ & ROS 2 Development",
        "category": "Robotics",
        "prerequisites": ["python_core"],
        "resources": [
            {
                "id": "yt_ros_01",
                "title": "ROS 2 Full Course for Beginners (Robot Operating System)",
                "type": "video",
                "provider": "Articulated Robotics (YouTube)",
                "url": "https://www.youtube.com/playlist?list=PLunhqkrRNRhYAffV8JDiFOatQXuU-NwGE",
                "duration_hours": 14,
                "difficulty": "intermediate",
                "skills_covered": ["cpp_ros"],
                "rating": 4.98,
                "is_free": True
            },
            {
                "id": "yt_ros_02",
                "title": "C++ Full Programming Course for Beginners",
                "type": "video",
                "provider": "freeCodeCamp / The Cherno (YouTube)",
                "url": "https://www.youtube.com/watch?v=vLnPwxZdW4Y",
                "duration_hours": 30,
                "difficulty": "beginner",
                "skills_covered": ["cpp_ros"],
                "rating": 4.95,
                "is_free": True
            }
        ]
    },
    "embedded_sys": {
        "id": "embedded_sys",
        "name": "Embedded Microcontrollers & Microprocessors",
        "category": "Hardware",
        "prerequisites": ["c_embedded"],
        "resources": [
            {
                "id": "yt_emb_01",
                "title": "STM32 Microcontroller Firmware & Hardware Design",
                "type": "video",
                "provider": "Phil's Lab (YouTube)",
                "url": "https://www.youtube.com/c/PhilsLab",
                "duration_hours": 16,
                "difficulty": "intermediate",
                "skills_covered": ["embedded_sys"],
                "rating": 4.97,
                "is_free": True
            }
        ]
    },
    "c_embedded": {
        "id": "c_embedded",
        "name": "Embedded C & Data Structures",
        "category": "Hardware",
        "prerequisites": [],
        "resources": [
            {
                "id": "yt_c_01",
                "title": "C Programming & Pointers Masterclass",
                "type": "video",
                "provider": "Neso Academy (YouTube)",
                "url": "https://www.youtube.com/playlist?list=PLBlnK6fEyqRggZZgYpPMUxdY1CYkZtARR",
                "duration_hours": 20,
                "difficulty": "beginner",
                "skills_covered": ["c_embedded"],
                "rating": 4.96,
                "is_free": True
            }
        ]
    },
    "control_theory": {
        "id": "control_theory",
        "name": "Control Systems (PID, State-Space)",
        "category": "Robotics/EE",
        "prerequisites": ["math_stats"],
        "resources": [
            {
                "id": "yt_ctrl_01",
                "title": "Control Bootcamp & Dynamical Systems",
                "type": "video",
                "provider": "Steve Brunton (YouTube / UW)",
                "url": "https://www.youtube.com/c/SteveBruntonControl",
                "duration_hours": 14,
                "difficulty": "intermediate",
                "skills_covered": ["control_theory"],
                "rating": 4.99,
                "is_free": True
            }
        ]
    },
    "math_kinematics": {
        "id": "math_kinematics",
        "name": "Linear Algebra & Kinematics",
        "category": "Robotics",
        "prerequisites": ["math_stats"],
        "resources": [
            {
                "id": "yt_kin_01",
                "title": "Robot Kinematics & Transformation Matrices",
                "type": "video",
                "provider": "Angela Sodemann (YouTube)",
                "url": "https://www.youtube.com/c/AngelaSodemann",
                "duration_hours": 10,
                "difficulty": "intermediate",
                "skills_covered": ["math_kinematics"],
                "rating": 4.9,
                "is_free": True
            }
        ]
    },
    "linux_sys": {
        "id": "linux_sys",
        "name": "Linux Systems Administration & Shell Scripting",
        "category": "Systems",
        "prerequisites": [],
        "resources": [
            {
                "id": "yt_linux_01",
                "title": "Linux Command Line & Bash Scripting Course",
                "type": "video",
                "provider": "NetworkChuck (YouTube)",
                "url": "https://www.youtube.com/c/NetworkChuck",
                "duration_hours": 8,
                "difficulty": "beginner",
                "skills_covered": ["linux_sys"],
                "rating": 4.95,
                "is_free": True
            }
        ]
    },
    "docker_k8s": {
        "id": "docker_k8s",
        "name": "Docker Containers & Kubernetes",
        "category": "DevOps",
        "prerequisites": ["linux_sys"],
        "resources": [
            {
                "id": "yt_k8s_01",
                "title": "Docker & Kubernetes Full Course for Beginners",
                "type": "video",
                "provider": "TechWorld with Nana (YouTube)",
                "url": "https://www.youtube.com/c/TechWorldwithNana",
                "duration_hours": 12,
                "difficulty": "intermediate",
                "skills_covered": ["docker_k8s"],
                "rating": 4.98,
                "is_free": True
            }
        ]
    },
    "verilog_sv": {
        "id": "verilog_sv",
        "name": "Verilog & SystemVerilog RTL",
        "category": "Semiconductors",
        "prerequisites": ["digital_electronics"],
        "resources": [
            {
                "id": "yt_vlsi_01",
                "title": "Verilog HDL & Digital Design Course",
                "type": "video",
                "provider": "Neso Academy (YouTube)",
                "url": "https://www.youtube.com/c/nesoacademy",
                "duration_hours": 16,
                "difficulty": "intermediate",
                "skills_covered": ["verilog_sv"],
                "rating": 4.94,
                "is_free": True
            }
        ]
    },
    "digital_electronics": {
        "id": "digital_electronics",
        "name": "Digital Electronics & Circuit Diagnostics",
        "category": "Hardware",
        "prerequisites": [],
        "resources": [
            {
                "id": "yt_dig_01",
                "title": "Digital Electronics Tutorials & Logic Gates",
                "type": "video",
                "provider": "Ben Eater (YouTube)",
                "url": "https://www.youtube.com/user/beneater",
                "duration_hours": 15,
                "difficulty": "beginner",
                "skills_covered": ["digital_electronics"],
                "rating": 4.99,
                "is_free": True
            }
        ]
    },
    "edge_ai": {
        "id": "edge_ai",
        "name": "Edge AI Quantization & TensorRT",
        "category": "AI/Hardware",
        "prerequisites": ["deep_learning", "c_embedded"],
        "resources": [
            {
                "id": "yt_edge_01",
                "title": "NVIDIA Jetson & TensorRT Edge AI Tutorials",
                "type": "video",
                "provider": "Paul McWhorter (YouTube)",
                "url": "https://www.youtube.com/c/PaulMcWhorter",
                "duration_hours": 18,
                "difficulty": "intermediate",
                "skills_covered": ["edge_ai"],
                "rating": 4.97,
                "is_free": True
            }
        ]
    },

    # ---- Previously-referenced-but-missing skills (civil/electrical/automotive/VLSI/cloud) ----
    # No static resources needed here -- retrieve_and_rank_resources() already injects
    # dynamic YouTube resources for any skill by name, so these just need real taxonomy
    # metadata (name/category/prerequisites) to stop skill-gap analysis and career matching
    # from silently going empty for careers that reference them.
    "aws_cloud": {"id": "aws_cloud", "name": "AWS / Cloud Architecture", "category": "Cloud", "prerequisites": ["linux_sys"], "resources": []},
    "bess_storage": {"id": "bess_storage", "name": "Grid Energy Storage & Battery Tech", "category": "Energy", "prerequisites": ["power_systems"], "resources": []},
    "bim_revit": {"id": "bim_revit", "name": "BIM & Autodesk Revit Structure", "category": "Civil", "prerequisites": [], "resources": []},
    "cad_modeling": {"id": "cad_modeling", "name": "3D CAD Modeling (SolidWorks/Fusion360)", "category": "Mechanical", "prerequisites": [], "resources": []},
    "cicd_pipelines": {"id": "cicd_pipelines", "name": "CI/CD Pipeline Automation", "category": "DevOps", "prerequisites": ["docker_k8s"], "resources": []},
    "comm_protocols": {"id": "comm_protocols", "name": "Hardware Communication Protocols (SPI, I2C, CAN, UART)", "category": "Hardware", "prerequisites": ["digital_electronics"], "resources": []},
    "computer_vision": {"id": "computer_vision", "name": "Computer Vision & OpenCV", "category": "AI/ML", "prerequisites": ["python_core"], "resources": []},
    "digital_design": {"id": "digital_design", "name": "Digital Logic & Computer Architecture", "category": "Semiconductors", "prerequisites": ["digital_electronics"], "resources": []},
    "etabs_staad": {"id": "etabs_staad", "name": "ETABS / STAAD Pro FEA Modeling", "category": "Civil", "prerequisites": ["solid_mechanics"], "resources": []},
    "etap_pvsyst": {"id": "etap_pvsyst", "name": "ETAP & PVSyst Simulation Tools", "category": "Energy", "prerequisites": ["power_systems"], "resources": []},
    "ev_powertrain": {"id": "ev_powertrain", "name": "EV Powertrain & Battery Management", "category": "Automotive", "prerequisites": ["matlab_simulink"], "resources": []},
    "fpga_prototyping": {"id": "fpga_prototyping", "name": "FPGA Synthesis (Xilinx / Altera)", "category": "Semiconductors", "prerequisites": ["verilog_sv"], "resources": []},
    "high_voltage": {"id": "high_voltage", "name": "Substations & High Voltage Protection", "category": "Energy", "prerequisites": ["power_systems"], "resources": []},
    "matlab_simulink": {"id": "matlab_simulink", "name": "MATLAB & Simulink Model-Based Design", "category": "Automotive/EE", "prerequisites": ["math_stats"], "resources": []},
    "microcontrollers": {"id": "microcontrollers", "name": "ARM Cortex Architecture & Registers", "category": "Hardware", "prerequisites": ["c_embedded"], "resources": []},
    "mlops": {"id": "mlops", "name": "MLOps, Docker & Model Deployment", "category": "AI/ML", "prerequisites": ["deep_learning", "docker_k8s"], "resources": []},
    "power_systems": {"id": "power_systems", "name": "Power Systems & Load Flow Analysis", "category": "Energy", "prerequisites": ["math_stats"], "resources": []},
    "rtos": {"id": "rtos", "name": "Real-Time Operating Systems (FreeRTOS)", "category": "Hardware", "prerequisites": ["c_embedded"], "resources": []},
    "seismic_eng": {"id": "seismic_eng", "name": "Seismic & Wind Dynamic Analysis", "category": "Civil", "prerequisites": ["solid_mechanics"], "resources": []},
    "solar_wind_design": {"id": "solar_wind_design", "name": "Solar PV & Wind Farm Engineering", "category": "Energy", "prerequisites": ["power_systems"], "resources": []},
    "solid_mechanics": {"id": "solid_mechanics", "name": "Mechanics of Materials & Structural Analysis", "category": "Civil", "prerequisites": ["math_stats"], "resources": []},
    "sta_timing": {"id": "sta_timing", "name": "Static Timing Analysis & EDA Tools", "category": "Semiconductors", "prerequisites": ["digital_design"], "resources": []},
    "steel_concrete_design": {"id": "steel_concrete_design", "name": "Reinforced Concrete & Steel Design Codes", "category": "Civil", "prerequisites": ["solid_mechanics"], "resources": []},
    "terraform": {"id": "terraform", "name": "Infrastructure as Code (Terraform)", "category": "DevOps", "prerequisites": ["linux_sys"], "resources": []},
    "uvm_verification": {"id": "uvm_verification", "name": "UVM Verification Frameworks", "category": "Semiconductors", "prerequisites": ["verilog_sv"], "resources": []},
    "vehicle_dynamics": {"id": "vehicle_dynamics", "name": "Vehicle Dynamics & Chassis Engineering", "category": "Automotive", "prerequisites": ["matlab_simulink"], "resources": []},

    # ---- Broadened-catalog skills (data / web / security / mech / power / bio / aero / chem / iot / qa) ----
    "sql": {"id": "sql", "name": "SQL & Data Modeling", "category": "Data", "prerequisites": [], "resources": []},
    "data_pipelines": {"id": "data_pipelines", "name": "Data Engineering & ETL Pipelines", "category": "Data", "prerequisites": ["sql", "python_core"], "resources": []},
    "spark_bigdata": {"id": "spark_bigdata", "name": "Distributed Data Processing (Spark)", "category": "Data", "prerequisites": ["data_pipelines"], "resources": []},
    "javascript": {"id": "javascript", "name": "JavaScript & TypeScript", "category": "Web", "prerequisites": [], "resources": []},
    "react_frontend": {"id": "react_frontend", "name": "React & Modern Front-End", "category": "Web", "prerequisites": ["javascript"], "resources": []},
    "nodejs_backend": {"id": "nodejs_backend", "name": "Node.js & Backend Services", "category": "Web", "prerequisites": ["javascript"], "resources": []},
    "rest_apis": {"id": "rest_apis", "name": "REST / GraphQL API Design", "category": "Web", "prerequisites": ["nodejs_backend"], "resources": []},
    "databases": {"id": "databases", "name": "SQL & NoSQL Databases", "category": "Web", "prerequisites": ["sql"], "resources": []},
    "network_security": {"id": "network_security", "name": "Networking & Network Security", "category": "Security", "prerequisites": ["linux_sys"], "resources": []},
    "cryptography": {"id": "cryptography", "name": "Applied Cryptography", "category": "Security", "prerequisites": ["math_stats"], "resources": []},
    "pentesting": {"id": "pentesting", "name": "Offensive Security & Pen Testing", "category": "Security", "prerequisites": ["network_security"], "resources": []},
    "gd_t": {"id": "gd_t", "name": "GD&T & Tolerance Analysis", "category": "Mechanical", "prerequisites": ["cad_modeling"], "resources": []},
    "fea_analysis": {"id": "fea_analysis", "name": "Finite Element Analysis (FEA)", "category": "Mechanical", "prerequisites": ["solid_mechanics"], "resources": []},
    "thermodynamics": {"id": "thermodynamics", "name": "Thermodynamics & Heat Transfer", "category": "Mechanical", "prerequisites": ["math_stats"], "resources": []},
    "protective_relaying": {"id": "protective_relaying", "name": "Protection & Relay Coordination", "category": "Energy", "prerequisites": ["power_systems"], "resources": []},
    "power_electronics": {"id": "power_electronics", "name": "Power Electronics & Converters", "category": "Energy", "prerequisites": ["digital_electronics"], "resources": []},
    "biomaterials": {"id": "biomaterials", "name": "Biomedical Instrumentation & Sensors", "category": "Biomedical", "prerequisites": ["digital_electronics"], "resources": []},
    "signal_processing": {"id": "signal_processing", "name": "Biosignal & Digital Signal Processing", "category": "Biomedical", "prerequisites": ["math_stats"], "resources": []},
    "medical_imaging": {"id": "medical_imaging", "name": "Medical Imaging Fundamentals", "category": "Biomedical", "prerequisites": ["signal_processing"], "resources": []},
    "aerodynamics": {"id": "aerodynamics", "name": "Aerodynamics & Fluid Mechanics", "category": "Aerospace", "prerequisites": ["math_stats"], "resources": []},
    "flight_dynamics": {"id": "flight_dynamics", "name": "Flight Dynamics & Control", "category": "Aerospace", "prerequisites": ["aerodynamics"], "resources": []},
    "propulsion": {"id": "propulsion", "name": "Propulsion Systems", "category": "Aerospace", "prerequisites": ["thermodynamics"], "resources": []},
    "process_simulation": {"id": "process_simulation", "name": "Process Simulation (Aspen/DWSIM)", "category": "Chemical", "prerequisites": ["thermodynamics"], "resources": []},
    "reaction_engineering": {"id": "reaction_engineering", "name": "Reaction Engineering & Kinetics", "category": "Chemical", "prerequisites": ["math_stats"], "resources": []},
    "process_control": {"id": "process_control", "name": "Process Dynamics & Control", "category": "Chemical", "prerequisites": ["control_theory"], "resources": []},
    "iot_protocols": {"id": "iot_protocols", "name": "IoT Connectivity & Protocols (MQTT, BLE, LoRa)", "category": "IoT", "prerequisites": ["comm_protocols"], "resources": []},
    "cloud_iot": {"id": "cloud_iot", "name": "Cloud IoT Platforms & Ingestion", "category": "IoT", "prerequisites": ["linux_sys"], "resources": []},
    "test_automation": {"id": "test_automation", "name": "Test Strategy & Automation Frameworks", "category": "Quality", "prerequisites": ["python_core"], "resources": []},
    "selenium_cypress": {"id": "selenium_cypress", "name": "UI Automation (Selenium/Cypress/Playwright)", "category": "Quality", "prerequisites": ["test_automation"], "resources": []},
    "ci_testing": {"id": "ci_testing", "name": "Continuous Integration for Test Suites", "category": "Quality", "prerequisites": ["test_automation"], "resources": []},
    "statistics": {"id": "statistics", "name": "Statistics & Inference", "category": "Data", "prerequisites": ["math_stats"], "resources": []},
    "data_viz": {"id": "data_viz", "name": "Data Visualization & Communication", "category": "Data", "prerequisites": ["python_core"], "resources": []},
    "experiment_design": {"id": "experiment_design", "name": "Experiment Design & A/B Testing", "category": "Data", "prerequisites": ["statistics"], "resources": []},
}

QUIZZES_DATABASE = {
    "python_core": {
        "assessment_id": "quiz_python_core",
        "skill_id": "python_core",
        "skill_name": "Advanced Python & Scientific Computing",
        "title": "Python Core Diagnostics",
        "description": "Evaluate Python data structures, list comprehensions, decorators, and memory references.",
        "questions": [
            {
                "id": "q1",
                "question_text": "What will be the output of `list(map(lambda x: x**2, filter(lambda x: x%2==0, range(5))))`?",
                "options": ["[0, 4, 16]", "[0, 4]", "[1, 9]", "[0, 2, 4]"],
                "correct_option_index": 0,
                "explanation": "filter keeps even numbers [0, 2, 4]. map squares them to [0, 4, 16]."
            },
            {
                "id": "q2",
                "question_text": "In Python, which built-in decorator is used to define a method that operates on the class itself rather than an instance?",
                "options": ["@staticmethod", "@classmethod", "@property", "@abstractmethod"],
                "correct_option_index": 1,
                "explanation": "@classmethod receives the class 'cls' as its first argument."
            }
        ]
    },
    "machine_learning": {
        "assessment_id": "quiz_machine_learning",
        "skill_id": "machine_learning",
        "skill_name": "Classical Machine Learning",
        "title": "ML Fundamentals Quiz",
        "description": "Assess knowledge of supervised vs unsupervised learning, bias-variance tradeoff, and evaluation metrics.",
        "questions": [
            {
                "id": "q1",
                "question_text": "What condition leads to high variance (overfitting) in a machine learning model?",
                "options": [
                    "Model is too simple and underfits training data",
                    "Model performs exceptionally on training data but poorly on unseen test data",
                    "High regularization penalty (L2 lambda)",
                    "Data sample size is infinitely large"
                ],
                "correct_option_index": 1,
                "explanation": "High variance means the model has memorized training noise and fails to generalize."
            }
        ]
    },
    "cpp_ros": {
        "assessment_id": "quiz_cpp_ros",
        "skill_id": "cpp_ros",
        "skill_name": "C++ & ROS 2 Development",
        "title": "ROS 2 & C++ Diagnostics",
        "description": "Evaluate understanding of ROS 2 nodes, topics, services, and modern C++ smart pointers.",
        "questions": [
            {
                "id": "q1",
                "question_text": "Which ROS 2 communication paradigm is best suited for non-blocking asynchronous streaming telemetry (e.g. sensor data)?",
                "options": ["ROS 2 Services (Request/Response)", "ROS 2 Topics (Publish/Subscribe)", "ROS 2 Actions", "ROS 2 Parameters"],
                "correct_option_index": 1,
                "explanation": "Topics (Pub/Sub) provide continuous, non-blocking asynchronous data streams ideal for sensors."
            }
        ]
    }
}
