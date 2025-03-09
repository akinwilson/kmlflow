import torch

'''
Generate Key object on either Validator or Node 

Poc stage 

using homomorphic commit scheme 
'''

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
Q= 36028797018963913 # prime within signed64
SEED = 1666
DIM = 30 




class Key:
    # sk_vec = torch.randint(0, Q, (1,DIM), dtype=torch.int64).to(device)
    # A = torch.randint(0, Q, (DIM,DIM), dtype=torch.int64).to(device)

    def __init__ (self,A=None.sk=None,q=Q,dim=DIM ):

        self.A = A if A is not None else self._gen_invertable_A()
        self.sk = sk if sk is not None else torch.randint(0, Q, (1,DIM), dtype=torch.int64).to(device)


    def _gen_invertable_A(self):
        while True:
            A = torch.randint(0, Q, (DIM,DIM), dtype=torch.int64).to(device)
            try:
                torch.inverse(A.float())
                return A
            except RuntimeError:
                continue # if singular
    
    def _commit_vector(self):
        r = torch.randint( 0, Q, (1,DIM), device=device).float()*0.01
        b_prime = ((self.A.float() @ self.sk.float() + r ) % self.q).long()
        return b_prime

    def pk(self):
        b = ((self.sk.float() @ self.A.float()  + torch.randint( 0, Q, (1,DIM), device=device).float()*0.01) % Q).long()
        return {"A":self.A, "b":self._commit_vector()}

    def sk(self):
        return self.sk

