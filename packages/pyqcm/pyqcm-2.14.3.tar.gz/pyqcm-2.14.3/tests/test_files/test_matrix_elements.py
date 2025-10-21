import pyqcm
from model_graphene_bath import model

# print(model.clus[0].cluster_model.matrix_elements('tb1'))
print('matrix elements of eb1:')
print(model.clus[0].cluster_model.matrix_elements('eb1'))
print('matrix elements of tb1:')
print(model.clus[0].cluster_model.matrix_elements('tb1'))

model.set_parameters("""
U = 4
t = 1
eb1_1=1
tb1_1=0.5
eb2_1=-1*eb1_1
tb2_1=1*tb1_1
"""
)
model.set_target_sectors("N6:S0")
I = pyqcm.model_instance(model)

print('\nmatrix elements of the interactions:\n', I.interactions())

print('\nParameters:\n', I.parameters())

print('\ncluster hoppint matrix:\n', I.cluster_hopping_matrix())

print('\ncluster hoppint matrix (with bath):\n', I.cluster_hopping_matrix(clus=0, full=True))

print('\nInstance parameters:\n', I.instance_parameters())
