import numpy as np
import math
import sopy_fem.globalvars as globalvars
from sopy_fem.initialization import initialization
from sopy_fem.solids_utils import Bmat_TR03, Calc_Bmat, derivCartesian, GiveNdof, GiveNnodes, giveElemVolume, FuncForm
from sopy_fem.dmat import dmat_Solids2D, giveLocalStiffness
from sopy_fem.gauss_quadrature import Set_Ngauss, GaussQuadrature


def assembly():
    stiff_assembly()
    loads_assembly()
    if(globalvars.data["ProblemType"] == "Structural_Mechanics" and globalvars.data["AnalysisType"] == "DynamicsAnalysis"):
        mass_assembly()

def stiff_assembly():
    mesh_type = globalvars.data["Mesh"]["ElemType"]
    for elem in globalvars.data["Mesh"]["Elements"]:
        if (mesh_type == "BAR02"):
            rigimat = stiffness_BAR02(elem)
        elif (mesh_type == "TRUSS02"):
            rigimat = stiffness_TRUSS02(elem)
        elif (mesh_type == "TR03"):
            rigimat = stiffness_TR03(elem)
        elif (mesh_type == "QU04"):
            rigimat = stiffness_QU04(elem)
        elif (mesh_type == "FRAME02"):
            rigimat = stiffness_FRAME02(elem)
        
        conec_list = elem["Connectivities"]
        doflist = np.zeros((len(conec_list)*globalvars.ndof), dtype=int)
        idof = 0
        for inode in range(len(conec_list)):
            id_node = conec_list[inode]-1
            for igl in range(globalvars.ndof):
                doflist[idof] =  globalvars.madgln[id_node, igl]
                idof += 1
        
        assamk(doflist, rigimat)

def mass_assembly():
    mesh_type = globalvars.data["Mesh"]["ElemType"]
    for elem in globalvars.data["Mesh"]["Elements"]:
        massMatrix= CalcMassMatrix(mesh_type, elem)
        conec_list = elem["Connectivities"]
        doflist = np.zeros((len(conec_list)*globalvars.ndof), dtype=int)
        idof = 0
        for inode in range(len(conec_list)):
            id_node = conec_list[inode]-1
            for igl in range(globalvars.ndof):
                doflist[idof] =  globalvars.madgln[id_node, igl]
                idof += 1
        
        assamMass(doflist, massMatrix)

    if ("Mass" in globalvars.data and (mesh_type == "FRAME02" or mesh_type == "TRUSS02")):
        massData = globalvars.data["Mass"]
        if("Lumped_Mass" in massData):
            for lumpedMass in massData["Lumped_Mass"]:
                node_id = lumpedMass["Node"] - 1
                if (mesh_type == "TRUSS02"):
                    doflist = np.zeros((globalvars.ndof), dtype=int)
                    massvec = np.zeros((globalvars.ndof), dtype=float)
                    idof = 0
                    for igl in range(2):
                        doflist[idof] = globalvars.madgln[node_id, igl]
                        massvec[idof] = lumpedMass["Traslational_mass"][igl]
                        idof += 1
                    assamMass(doflist, np.diag(massvec))
                elif (mesh_type == "FRAME02"):
                    doflist = np.zeros((globalvars.ndof * 3), dtype=int)
                    massvec = np.zeros((globalvars.ndof * 3), dtype=float)
                    idof = 0
                    for igl in range(3):
                        doflist[idof] = globalvars.madgln[node_id, igl]
                        if (igl < 2):
                            massvec[idof] = lumpedMass["Traslational_mass"][igl]
                        else:
                            massvec[idof] = lumpedMass["Rotational_mass"]
                        idof += 1
                    assamMass(doflist, np.diag(massvec))

        if("Line_Mass" in massData):
            for lineMass in massData["Line_Mass"]:
                assemblyFrame02LineMass(lineMass)

def loads_assembly():
    if ("Loads" in globalvars.data):
        Loads = globalvars.data["Loads"]
        elemType = globalvars.data["Mesh"]["ElemType"]

        if ("Point_Loads" in Loads):
            doflist = np.zeros((globalvars.ndof), dtype=int)
            fvect = np.zeros((globalvars.ndof), dtype=float)
            for pointLoad in Loads["Point_Loads"]:
                id_node = pointLoad["Node"] - 1
                idof = 0
                for igl in range(globalvars.ndof):
                    doflist[idof] = globalvars.madgln[id_node, igl]
                    fvect[idof] = pointLoad["Values"][igl]
                    idof += 1
                assamf(doflist, fvect)   

        if ("Line_Loads" in Loads):
            for lineLoad in Loads["Line_Loads"]:
                lineLoadsAssembly(lineLoad)

        if("Body_Loads" in Loads):
            for elemLoad in Loads["Body_Loads"]:
                bodyLoadsAssembly(elemLoad, elemType)

def dynamics_loads_assembly(t):
    globalvars.asload[:] = 0.0   
    if ("Dynamics_Loads" in globalvars.data):
        DynamicsLoads = globalvars.data["Dynamics_Loads"]
        if ("Harmonic_Point_Loads" in DynamicsLoads):
            doflist = np.zeros((globalvars.ndof), dtype=int)
            fvect = np.zeros((globalvars.ndof), dtype=float)
            for dynPointLoad in DynamicsLoads["Harmonic_Point_Loads"]:
                id_node = dynPointLoad["Node"] - 1
                idof = 0
                for igl in range(globalvars.ndof):
                    doflist[idof] = globalvars.madgln[id_node, igl]
                    frequency = dynPointLoad["Load_Frequency(Hz)"]
                    fact = math.sin(2.0*math.pi*frequency*t)
                    fvect[idof] = dynPointLoad["Amplitudes"][igl]*fact
                    idof += 1
                assamf(doflist, fvect)


def stiffness_BAR02(elem):
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    node1 = elem["Connectivities"][0] - 1
    x1 = globalvars.data["Mesh"]["Nodes"][node1]["x"]
    y1 = globalvars.data["Mesh"]["Nodes"][node1]["y"]
    node2 = elem["Connectivities"][1] - 1
    x2 = globalvars.data["Mesh"]["Nodes"][node2]["x"]
    y2 = globalvars.data["Mesh"]["Nodes"][node2]["y"]
    l = math.sqrt((x2 - x1)** 2 + (y2 - y1)** 2)
    k = giveLocalStiffness(material, l)
    rigimat = np.zeros((2, 2), dtype=float)
    rigimat[0, 0] = k
    rigimat[0, 1] = -k
    rigimat[1, 0] = -k
    rigimat[1, 1] = k
    return rigimat


def stiffness_TRUSS02(elem):
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    Young = material["Young"]
    Area = material["Area"]
    node1 = elem["Connectivities"][0] - 1
    x1 = globalvars.data["Mesh"]["Nodes"][node1]["x"]
    y1 = globalvars.data["Mesh"]["Nodes"][node1]["y"]
    node2 = elem["Connectivities"][1] - 1
    x2 = globalvars.data["Mesh"]["Nodes"][node2]["x"]
    y2 = globalvars.data["Mesh"]["Nodes"][node2]["y"]
    length = math.sqrt((x2 - x1)** 2 + (y2 - y1)** 2)
    cos_alpha = (x2 - x1) / length
    sin_alpha = (y2 - y1) / length
    
    k = Young * Area / length
    rigimat = np.zeros((4,4), dtype=float)
    rigimat[0, 0] = k * cos_alpha ** 2
    rigimat[0, 1] = k * cos_alpha * sin_alpha
    rigimat[0, 2] = -k * cos_alpha ** 2
    rigimat[0, 3] = -k * cos_alpha * sin_alpha
    rigimat[1, 0] = k*cos_alpha*sin_alpha
    rigimat[1, 1] = k * sin_alpha ** 2
    rigimat[1, 2] = -k * cos_alpha * sin_alpha
    rigimat[1, 3] = -k * sin_alpha ** 2
    rigimat[2, 0] = -k * cos_alpha ** 2
    rigimat[2, 1] = -k * cos_alpha * sin_alpha
    rigimat[2, 2] = k*cos_alpha** 2
    rigimat[2, 3] = k * cos_alpha * sin_alpha
    rigimat[3, 0] = -k * cos_alpha * sin_alpha
    rigimat[3, 1] = -k * sin_alpha ** 2
    rigimat[3, 2] = k * cos_alpha * sin_alpha
    rigimat[3, 3] = k * sin_alpha ** 2
    return rigimat

def stiffness_FRAME02(elem):
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    Young = material["Young"]
    Area = 1.0e-12
    Inertia = 1.0e-12
    if ("Area" in material and Inertia):
        Area = material["Area"]
        Inertia = material["Inertia"]
    if ("Width" in material and "Height" in material):
        Area = material["Width"] * material["Height"]
        Inertia = (material["Width"] * material["Height"]**3) / 12.0
    node1 = elem["Connectivities"][0] - 1
    x1 = globalvars.data["Mesh"]["Nodes"][node1]["x"]
    y1 = globalvars.data["Mesh"]["Nodes"][node1]["y"]
    node2 = elem["Connectivities"][1] - 1
    x2 = globalvars.data["Mesh"]["Nodes"][node2]["x"]
    y2 = globalvars.data["Mesh"]["Nodes"][node2]["y"]
    L = math.sqrt((x2 - x1)** 2 + (y2 - y1)** 2)
    c = (x2 - x1) / L
    s = (y2 - y1) / L
    
    EA = Young * Area
    EI = Young * Inertia
    rigimat = np.zeros((6,6), dtype=float)
    rigimat[0, 0] = EA * c ** 2 / L + 12 * EI * s ** 2 / L ** 3
    rigimat[0, 1] = EA * c * s / L - 12 * EI * c * s / L ** 3
    rigimat[0, 2] = -6 * EI * s / L ** 2
    rigimat[0, 3] = -EA * c ** 2 / L - 12 * EI * s ** 2 / L ** 3
    rigimat[0, 4] =  -EA * c * s / L + 12 * EI * c * s / L ** 3
    rigimat[0, 5] = -6 * EI * s / L ** 2

    rigimat[1, 0] = EA * c * s / L - 12 * EI * c * s / L ** 3
    rigimat[1, 1] = EA * s ** 2 / L + 12 * EI * c ** 2 / L ** 3
    rigimat[1, 2] = 6 * EI * c / L ** 2
    rigimat[1, 3] = -EA * c * s / L + 12 * EI * c * s / L ** 3
    rigimat[1, 4] = -EA *  s ** 2 / L -  12 * EI * c ** 2 / L ** 3
    rigimat[1, 5] = 6 * EI * c / L ** 2

    rigimat[2, 0] = -6 * EI * s / L ** 2
    rigimat[2, 1] = 6 * EI * c / L ** 2
    rigimat[2, 2] = 4 * EI / L
    rigimat[2, 3] = 6 * EI * s / L ** 2
    rigimat[2, 4] = -6 * EI * c / L ** 2
    rigimat[2, 5] = 2 * EI / L

    rigimat[3, 0] = -EA * c ** 2 / L - 12 * EI * s ** 2 / L ** 3
    rigimat[3, 1] = -EA * c * s / L + 12 * EI * c * s / L ** 3
    rigimat[3, 2] = 6 * EI * s / L ** 2
    rigimat[3, 3] = EA * c ** 2 / L + 12 * EI * s ** 2 / L ** 3
    rigimat[3, 4] = EA * c * s / L - 12 * EI * c  * s / L ** 3
    rigimat[3, 5] = 6 * EI * s / L ** 2

    rigimat[4, 0] = -EA * c * s / L + 12 * EI * c * s / L ** 3
    rigimat[4, 1] = -EA * s ** 2 / L - 12 * EI * c ** 2 / L ** 3
    rigimat[4, 2] = -6 * EI * c / L ** 2
    rigimat[4, 3] = EA * c * s / L - 12 * EI * c * s / L ** 3
    rigimat[4, 4] = EA * s ** 2 / L + 12 * EI * c ** 2 / L ** 3
    rigimat[4, 5] = -6 * EI * c / L ** 2

    rigimat[5, 0] = -6 * EI * s / L ** 2
    rigimat[5, 1] = 6 * EI * c / L ** 2
    rigimat[5, 2] = 2 * EI / L
    rigimat[5, 3] = 6 * EI * s / L ** 2
    rigimat[5, 4] = -6 * EI * c / L ** 2
    rigimat[5, 5] = 4 * EI / L

    return rigimat


def stiffness_TR03(elem):
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    Dmat = dmat_Solids2D(material)

    Bmat, Area = Bmat_TR03(elem)
    
    DmatxB = np.matmul(Dmat, Bmat)
    thickness = 1.0
    if(material["Plane_Type"] == "Plane_Stress"):
        thickness =material["Thickness"]
    rigimat = np.matmul(Bmat.transpose(), DmatxB) * Area * thickness
    return rigimat


def stiffness_QU04(elem):
    ProblemType = globalvars.data["ProblemType"]
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    Dmat = dmat_Solids2D(material)
    thickness = 1.0
    if(material["Plane_Type"] == "Plane_Stress"):
        thickness = material["Thickness"]
    Dmat *= thickness
    return stiffnessMatCalc(elem, "QU04", ProblemType, Dmat)

def stiffnessMatCalc(elem, ElemType, ProblemType, Dmat):
    ngauss = Set_Ngauss(ElemType)
    Nodes = globalvars.data["Mesh"]["Nodes"]
    ndof = GiveNdof(ElemType, ProblemType)
    nnodes = GiveNnodes(ElemType)
    size = nnodes * ndof
    rigimat = np.zeros((size,size), dtype=float)
    pos_pg, W = GaussQuadrature(ElemType)

    for igauss in range(ngauss):
        det_Jac, derivCart = derivCartesian(elem, ElemType, Nodes, pos_pg[igauss])
        Bmat = Calc_Bmat(ElemType, derivCart, ProblemType)
        DxBmat = np.matmul(Dmat, Bmat)
        rigimat_pg = np.matmul(Bmat.transpose(), DxBmat) * det_Jac * W[igauss]
        rigimat += rigimat_pg
    return rigimat

def CalcFrameMassMatrix(elem):
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    A = 1.0e-12
    if ("Area" in material):
        A = material["Area"]
    if ("Width" in material and "Height" in material):
        A = material["Width"] * material["Height"]
    rho = material["Density"]
    node1 = elem["Connectivities"][0] - 1
    x1 = globalvars.data["Mesh"]["Nodes"][node1]["x"]
    y1 = globalvars.data["Mesh"]["Nodes"][node1]["y"]
    node2 = elem["Connectivities"][1] - 1
    x2 = globalvars.data["Mesh"]["Nodes"][node2]["x"]
    y2 = globalvars.data["Mesh"]["Nodes"][node2]["y"]
    L = math.sqrt((x2 - x1)** 2 + (y2 - y1)** 2)
    c = (x2 - x1) / L
    s = (y2 - y1) / L
    
    massMatrix = np.zeros((6,6), dtype=float)
    massMatrix[0, 0] = A * L * c ** 2 * rho / 3 + 13 * A * L * rho * s ** 2 / 35
    massMatrix[0, 1] = -4 * A * L * rho * c * s / 105
    massMatrix[0, 2] = -11 * A * L ** 2 * rho * s / 210
    massMatrix[0, 3] = A * L * c ** 2 * rho / 6 + 9 * A * L * rho * s ** 2 / 70
    massMatrix[0, 4] = 4 * A * L * rho * c * s / 105
    massMatrix[0, 5] = 13 * A * L ** 2 * rho * s / 420
    massMatrix[1, 0] = -4 * A * L * rho * c * s / 105
    massMatrix[1, 1] = 13 * A * L * rho * c ** 2 / 35 + A * L * rho * s ** 2 / 3
    massMatrix[1, 2] = 11 * A * L ** 2 * rho * c / 210
    massMatrix[1, 3] = 4 * A * L * rho * c * s / 105
    massMatrix[1, 4] = 9 * A * L * rho * c ** 2 / 70 + A * L * rho * s ** 2 / 6
    massMatrix[1, 5] = -13 * A * L ** 2 * rho * c / 420
    massMatrix[2, 0] = -11 * A * L ** 2 * rho * s / 210
    massMatrix[2, 1] = 11 * A * L ** 2 * rho * c / 210
    massMatrix[2, 2] = A * L ** 3 * rho / 105
    massMatrix[2, 3] = -13 * A * L ** 2 * rho * s / 420
    massMatrix[2, 4] = 13 * A * L ** 2 * rho * c / 420
    massMatrix[2, 5] = -A * L ** 3 * rho / 140
    massMatrix[3, 0] = A * L * c ** 2 * rho / 6 + 9 * A * L * rho * s ** 2 / 70
    massMatrix[3, 1] = 4 * A * L * rho * c * s / 105
    massMatrix[3, 2] = -13 * A * L ** 2 * rho * s / 420
    massMatrix[3, 3] = A * L * c ** 2 * rho / 3 + 13 * A * L * rho * s ** 2 / 35
    massMatrix[3, 4] = -4 * A * L * rho * c * s / 105
    massMatrix[3, 5] = 11 * A * L ** 2 * rho * s / 210
    massMatrix[4, 0] = 4 * A * L * rho * c * s / 105
    massMatrix[4, 1] = 9 * A * L * rho * c ** 2 / 70 + A * L * rho * s ** 2 / 6
    massMatrix[4, 2] = 13 * A * L ** 2 * rho * c / 420
    massMatrix[4, 3] = -4 * A * L * rho * c * s / 105
    massMatrix[4, 4] = 13 * A * L * rho * c ** 2 / 35 + A * L * rho * s ** 2 / 3
    massMatrix[4, 5] = -11 * A * L ** 2 * rho * c / 210
    massMatrix[5, 0] = 13 * A * L ** 2 * rho * s / 420
    massMatrix[5, 1] = -13 * A * L ** 2 * rho * c / 420
    massMatrix[5, 2] = -A * L ** 3 * rho / 140
    massMatrix[5, 3] = 11 * A * L ** 2 * rho * s / 210
    massMatrix[5, 4] = -11 * A * L ** 2 * rho * c / 210
    massMatrix[5, 5] = A * L ** 3 * rho / 105

    return massMatrix

def CalcMassMatrix(ElemType, elem):
    if(ElemType == "FRAME02"):
        massMatrix = CalcFrameMassMatrix(elem)
    else:
        massMatrix = CalcGenericMassMatrix(ElemType, elem)
    return massMatrix


def CalcGenericMassMatrix(ElemType, elem):
    nnodes = GiveNnodes(ElemType)
    ngauss = Set_Ngauss(ElemType)
    mat_id = elem["MaterialId"] - 1
    material = globalvars.data["Materials"][mat_id]
    Nodes = globalvars.data["Mesh"]["Nodes"]
    pos_pg, W = GaussQuadrature(ElemType)
 
    if(globalvars.data["ProblemType"] == "Thermal"):
        rho = material["Specific_Heat"]
        nrows = nnodes
        ncols = nnodes
        ngl = 1
    elif(globalvars.data["ProblemType"] == "Structural_Mechanics"):
        rho = material["Density"]
        if (ElemType == "BAR02"):
            nrows = nnodes
            ncols = nnodes
            ngl = 1
        else:
            nrows = nnodes * 2
            ncols = nnodes * 2
            ngl = 2
        
        if (ElemType == "BAR02" or ElemType == "TRUSS02"):
            rho *= material["Area"]
        elif(ElemType == "TR03" or ElemType == "TR06" or ElemType == "QU04" or ElemType == "QU08" or ElemType == "QU09"):
            thickness = 1.0
            if(material["Plane_Type"] == "Plane_Stress"):
                thickness = material["Thickness"]
            rho *= thickness

    massMatrix = np.zeros((nrows,ncols), dtype=float)
    localMat = np.zeros((ngl,ngl), dtype=float)
    massMatrix_pg = np.zeros((ngl,ngl), dtype=float)

    for inode in range(nnodes):
        for jnode in range(nnodes):
            irow_ini = inode * ngl
            irow_end = irow_ini + ngl
            icol_ini = jnode * ngl
            icol_end = icol_ini + ngl
            for igauss in range(ngauss):
                fform = FuncForm(ElemType, pos_pg, igauss)
                for igl in range(ngl):
                    localMat[igl,igl] = fform[inode] * fform[jnode]
                det_Jac, _ = derivCartesian(elem, ElemType, Nodes, pos_pg[igauss])
                massMatrix_pg[:ngl,:ngl] = localMat[:ngl,:ngl]* rho * W[igauss] * det_Jac
                massMatrix[irow_ini:irow_end,icol_ini:icol_end] += massMatrix_pg[:ngl,:ngl]
    return massMatrix

def assemblyFrame02LineMass(lineMass):
    nodeIni_idx = lineMass["Node_ini"] - 1
    x1 = globalvars.data["Mesh"]["Nodes"][nodeIni_idx]["x"]
    y1 = globalvars.data["Mesh"]["Nodes"][nodeIni_idx]["y"]
    nodeEnd_idx = lineMass ["Node_end"] - 1
    x2 = globalvars.data["Mesh"]["Nodes"][nodeEnd_idx]["x"]
    y2 = globalvars.data["Mesh"]["Nodes"][nodeEnd_idx]["y"]
    nodeList = [nodeIni_idx, nodeEnd_idx]
    L = math.sqrt((x2 - x1)** 2 + (y2 - y1)** 2)
    c = (x2 - x1) / L
    s = (y2 - y1) / L

    mass = lineMass["Mass_per_Length"]
    
    massMatrix = np.zeros((6,6), dtype=float)
    massMatrix[0, 0] = mass * L * c ** 2 / 3 + 13 * mass * L * s ** 2 / 35
    massMatrix[0, 1] = -4 * mass * L * c * s / 105
    massMatrix[0, 2] = -11 * mass * L ** 2 * s / 210
    massMatrix[0, 3] = mass * L * c ** 2 / 6 + 9 * mass * L * s ** 2 / 70
    massMatrix[0, 4] = 4 * mass * L * c * s / 105
    massMatrix[0, 5] = 13 * mass * L ** 2 * s / 420
    massMatrix[1, 0] = -4 * mass * L * c * s / 105
    massMatrix[1, 1] = 13 * mass * L * c ** 2 / 35 + mass * L * s ** 2 / 3
    massMatrix[1, 2] = 11 * mass * L ** 2 * c / 210
    massMatrix[1, 3] = 4 * mass * L * c * s / 105
    massMatrix[1, 4] = 9 * mass * L * c ** 2 / 70 + mass * L * s ** 2 / 6
    massMatrix[1, 5] = -13 * mass * L ** 2 * c / 420
    massMatrix[2, 0] = -11 * mass * L ** 2  * s / 210
    massMatrix[2, 1] = 11 * mass * L ** 2 * c / 210
    massMatrix[2, 2] = mass * L ** 3  / 105
    massMatrix[2, 3] = -13 * mass * L ** 2 * s / 420
    massMatrix[2, 4] = 13 * mass * L ** 2 * c / 420
    massMatrix[2, 5] = -mass * L ** 3 / 140
    massMatrix[3, 0] = mass * L * c ** 2 / 6 + 9 * mass * L * s ** 2 / 70
    massMatrix[3, 1] = 4 * mass * L * c * s / 105
    massMatrix[3, 2] = -13 * mass * L ** 2 * s / 420
    massMatrix[3, 3] = mass * L * c ** 2 / 3 + 13 * mass * L * s ** 2 / 35
    massMatrix[3, 4] = -4 * mass * L * c * s / 105
    massMatrix[3, 5] = 11 * mass * L ** 2 * s / 210
    massMatrix[4, 0] = 4 * mass * L * c * s / 105
    massMatrix[4, 1] = 9 * mass * L * c ** 2 / 70 + mass * L * s ** 2 / 6
    massMatrix[4, 2] = 13 * mass * L ** 2 * c / 420
    massMatrix[4, 3] = -4 * mass * L * c * s / 105
    massMatrix[4, 4] = 13 * mass * L * c ** 2 / 35 + mass * L * s ** 2 / 3
    massMatrix[4, 5] = -11 * mass * L ** 2 * c / 210
    massMatrix[5, 0] = 13 * mass * L ** 2 * s / 420
    massMatrix[5, 1] = -13 * mass * L ** 2 * c / 420
    massMatrix[5, 2] = -mass * L ** 3  / 140
    massMatrix[5, 3] = 11 * mass * L ** 2 * s / 210
    massMatrix[5, 4] = -11 * mass * L ** 2 * c / 210
    massMatrix[5, 5] = mass * L ** 3 / 105


    doflist = np.zeros((6, ), dtype=int)
    idof = 0
    for node in nodeList:
        for igl in range(3):
            doflist[idof] = globalvars.madgln[node, igl]
            idof += 1

    assamMass(doflist, massMatrix)


def bodyLoadsAssembly(elemLoad, elemType):
    elemIndex = elemLoad["Elem"] -1
    elem = globalvars.data["Mesh"]["Elements"][elemIndex]
    qvec = np.zeros((globalvars.ndof), dtype=float)
    nnodes = GiveNnodes(elemType)
    volume = giveElemVolume(elem, elemType)
    fact = volume/float(nnodes) #This operation is only valid for linear elements
    if("qx" in elemLoad):
        qvec[0]=elemLoad["qx"]*fact
    if(globalvars.ndof==2):
        if("qy" in elemLoad):
            qvec[1]=elemLoad["qy"] * fact

    doflist = np.zeros((globalvars.ndof), dtype=int)
    fvect = np.zeros((globalvars.ndof), dtype=float)
    for node in elem["Connectivities"]:
        id_node =node - 1
        idof = 0
        for igl in range(globalvars.ndof):
            doflist[idof] = globalvars.madgln[id_node, igl]
            fvect[idof] = qvec[igl]
            idof += 1
        assamf(doflist, fvect) 

def lineLoadsAssembly(lineLoad):
    elemType = globalvars.data["Mesh"]["ElemType"]

    nodeIni_idx = lineLoad["Node_ini"] - 1
    x1 = globalvars.data["Mesh"]["Nodes"][nodeIni_idx]["x"]
    y1 = globalvars.data["Mesh"]["Nodes"][nodeIni_idx]["y"]
    nodeEnd_idx = lineLoad["Node_end"] - 1
    x2 = globalvars.data["Mesh"]["Nodes"][nodeEnd_idx]["x"]
    y2 = globalvars.data["Mesh"]["Nodes"][nodeEnd_idx]["y"]
    nodeList = [nodeIni_idx, nodeEnd_idx]

    length = math.sqrt((x2 - x1)** 2 + (y2 - y1)** 2)

    if (elemType == "FRAME02"):
        qvec = np.zeros((globalvars.ndof * 2), dtype=float)
        if("qx" in lineLoad):
            qvec[0]=lineLoad["qx"]*0.5*length
            qvec[3]=lineLoad["qx"]*0.5*length
        if("qy" in lineLoad):
            qvec[1]=lineLoad["qy"]*0.5*length
            qvec[4]=lineLoad["qy"]*0.5*length
            qvec[2]=lineLoad["qy"]*length**2/12.0
            qvec[5]=-lineLoad["qy"]*length**2/12.0

        doflist = np.zeros((globalvars.ndof * 2), dtype=int)
        fvect = np.zeros((globalvars.ndof * 2), dtype=float)
        idof = 0
        for node in nodeList:
            for igl in range(globalvars.ndof):
                doflist[idof] = globalvars.madgln[node, igl]
                fvect[idof] = qvec[idof]
                idof += 1
        assamf(doflist, fvect)

    else:
        fact = 0.5*length
        qvec = np.zeros((globalvars.ndof), dtype=float)
        if("qx" in lineLoad):
            qvec[0]=lineLoad["qx"]*fact
        if(globalvars.ndof==2 ):
            if("qy" in lineLoad):
                qvec[1]=lineLoad["qy"]*fact

        doflist = np.zeros((globalvars.ndof), dtype=int)
        fvect = np.zeros((globalvars.ndof), dtype=float)
        for node in nodeList:
            idof = 0
            for igl in range(globalvars.ndof):
                doflist[idof] = globalvars.madgln[node, igl]
                fvect[idof] = qvec[igl]
                idof += 1
            assamf(doflist, fvect)  


def assamk(doflist, rigimat):
  ndof = len(doflist)
  for idofn in range(ndof):
      ipos = doflist[idofn]
      for jdofn in range(ndof):
        jpos = doflist[jdofn]
        globalvars.astiff[ipos, jpos] += rigimat[idofn, jdofn]

def assamMass(doflist, massmat):
  ndof = len(doflist)
  for idofn in range(ndof):
      ipos = doflist[idofn]
      for jdofn in range(ndof):
        jpos = doflist[jdofn]
        globalvars.amassmat[ipos, jpos] += massmat[idofn, jdofn]


def assamf(doflist, fvect):
  ndof = len(doflist)
  for idofn in range(ndof):
      ipos = doflist[idofn]
      globalvars.asload[ipos] += fvect[idofn]
