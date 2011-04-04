import os
from sympycore import Matrix
from sympycore.physics.sysbio import SteadyFluxAnalyzer

def test_sauro2004_fig3 ():
    network = SteadyFluxAnalyzer('''\
S1=>S2
ES=>S1+E
E+S2=>ES
''')
    #print network
    fluxes, kernel = network.get_kernel_GJE ()
    variables = fluxes[network.rank:]
    #print network.label_matrix (kernel, ['%s='%f for f in fluxes], variables)

def test_example_yeast():
    sbml_file = os.path.join (os.path.dirname (__file__),'yeast_example.xml')

    external_fluxes = dict(R_GL_in=100, R_FviP_out=11, R_GviP_out=3.8,
                           R_GiiiP_out=0.45, R_RvP_out=2.6,
                           R_OA_out=0.36, R_AcCoA_out=0.3,
                           R_ASP_out=2.39, R_ARG_out=1.94,
                           R_GLY_out=1.17, R_MET_out=0.51,
                           R_THR_out=1.54, R_ILE_out=2.33,
                           R_ASN_out=0.82, R_ALA_out=2.77,
                           R_GLU_out=3.04, R_GLN_out=1.06,
                           R_HIS_out=0.8, R_LEU_out=3.57,
                           R_LYS_out=3.45, R_PHE_out=2.43,
                           R_PRO_out=1.66, R_SER_out=1.12,
                           R_TRP_out=0.62, R_TYR_out=1.84,
                           R_VAL_out=2.66)
    internal_fluxes = dict(R_IOSm_IOSo=0, R_GviP_RLvP=5,
                           R_TCA_MAm_PYm=0, R_OA_PEP=0, R_B_THR_GLY=0, R_B_PY_AcCoA_LEU_M=2,
                           R_B_PY_VAL_M=1, R_ASPm_ASPo=2, R_PYo_AAo=10, R_B_GLT=4,
                           R_B_PY_ALA_M1=1.0, R_US_C_ASP_AS=2.5, R_OGo_OGm=0, )

    class ExampleYeast(SteadyFluxAnalyzer):
        def get_splitted_reactions(self):
            independent_flux_candidates = external_fluxes.keys()+internal_fluxes.keys()
            indep_cols = [i for i,v in enumerate (self.reactions) if v in independent_flux_candidates]
            return [j for j in range (len (self.reactions)) if j not in indep_cols], []

    network = ExampleYeast(sbml_file, discard_boundary_species = True)
    fluxes, kernelGJE = network.get_kernel_GJE()
    variablesGJE = fluxes[-kernelGJE.shape[1]:]
    fluxesSVD, kernelSVD = network.get_kernel_SVD()
    assert fluxes==fluxesSVD
    row_labels = ['%s='%f for f in fluxes if f not in variablesGJE]
    row_labels += ['%s[%s]='%(f,i) for i,f in enumerate(variablesGJE)]
    col_labels = ['%02d' %i for i,v in enumerate (variablesGJE)]

    print network.label_matrix (kernelGJE, row_labels, col_labels).__str__ (max_nrows=300, max_ncols=50)
    #print network.get_relation_GJE()[-1]
    #print network.get_relation_SVD()[-1]
    #print network.get_relation_SVD_error()
    #print network.sparsity
    #print network.sparsity_kernel_GJE
    #print network.sparsity_kernel_SVD
    #print network.condition_number
    #network.matrix_plot(kernelGJE, 'kernelGJE.pdf')
    #network.matrix_plot(kernelSVD.round (decimals=3), 'kernelSVD.pdf')
