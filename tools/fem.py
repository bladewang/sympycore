from sympycore.arithmetic.numbers import div
from sympycore import *

x,y,z = map(Symbol,'xyz')

class ReferenceSimplex:
   def __init__(self, nsd):
       self.nsd = nsd
       coords = []
       if nsd <= 3:
           coords = [x,y,z][:nsd]
       else:
           coords = []
           for d in range(0,nsd):
               coords.append(Symbol("x_%d" % d))
       self.coords = coords

   def integrate(self,f):
       coords = self.coords
       nsd = self.nsd

       limit = 1
       for p in coords:
           limit -= p

       intf = f
       for d in range(0,nsd):
           p = coords[d]
           limit += p
           intf = intf.expand().integrate((p, 0, limit))
       return intf

def bernstein_space(order, nsd):
   if nsd > 3:
       raise RuntimeError("Bernstein only implemented in 1D, 2D, and 3D")
   sum = 0
   basis = []
   coeff = []

   if nsd == 1:
       b1, b2 = x, 1-x
       for o1 in range(0,order+1):
           for o2 in range(0,order+1):
               if o1 + o2  == order:
                   aij = Symbol("a_%d_%d" % (o1,o2))
                   sum += aij*binomial(order,o1)*pow(b1, o1)*pow(b2, o2)
                   basis.append(binomial(order,o1)*pow(b1, o1)*pow(b2, o2))
                   coeff.append(aij)


   if nsd == 2:
       b1, b2, b3 = x, y, 1-x-y
       for o1 in range(0,order+1):
           for o2 in range(0,order+1):
               for o3 in range(0,order+1):
                   if o1 + o2 + o3 == order:
                       aij = Symbol("a_%d_%d_%d" % (o1,o2,o3))
                       fac = factorial(order)/ (factorial(o1)*factorial(o2)*factorial(o3))
                       sum += aij*fac*pow(b1, o1)*pow(b2, o2)*pow(b3, o3)
                       basis.append(fac*pow(b1, o1)*pow(b2, o2)*pow(b3, o3))
                       coeff.append(aij)

   if nsd == 3:
       b1, b2, b3, b4 = x, y, z, 1-x-y-z
       for o1 in range(0,order+1):
           for o2 in range(0,order+1):
               for o3 in range(0,order+1):
                   for o4 in range(0,order+1):
                       if o1 + o2 + o3 + o4 == order:
                           aij = Symbol("a_%d_%d_%d_%d" % (o1,o2,o3,o4))
                           fac = factorial(order)/ (factorial(o1)*factorial(o2)*factorial(o3)*factorial(o4))
                           sum += aij*fac*pow(b1, o1)*pow(b2, o2)*pow(b3, o3)*pow(b4, o4)
                           basis.append(fac*pow(b1, o1)*pow(b2, o2)*pow(b3, o3)*pow(b4, o4))
                           coeff.append(aij)


   return sum, coeff, basis

def create_point_set(order, nsd):
   h = Rational(1,order)
   set = []

   if nsd == 1:
       for i in range(0, order+1):
           x = i*h
           if x <= 1:
               set.append((x,y))

   if nsd == 2:
       for i in range(0, order+1):
           x = i*h
           for j in range(0, order+1):
               y = j*h
               if x + y <= 1:
                  set.append((x,y))

   if nsd == 3:
       for i in range(0, order+1):
           x = i*h
           for j in range(0, order+1):
               y = j*h
               for k in range(0, order+1):
                   z = j*h
                   if x + y + z  <= 1:
                       set.append((x,y,z))

   return set



def create_matrix(equations, coeffs):
   A = Matrix(len(equations))
   i = 0;  j = 0
   for j in range(0, len(coeffs)):
       c = coeffs[j]
       for i in range(0, len(equations)):
           e = equations[i]
           r = (e/c).expand()
           if r.is_Add:
              r = r.data.get(r.one, 0)
           elif r.is_Number:
              r = r.data
           else:
              r = 0
           A[i,j] = r
   return A

class Lagrange:
   def __init__(self,nsd, order):
       self.nsd = nsd
       self.order = order
       self.compute_basis()

   def nbf(self):
       return len(self.N)

   def compute_basis(self):
       order = self.order
       nsd = self.nsd
       N = []
       pol, coeffs, basis = bernstein_space(order, nsd)
       points = create_point_set(order, nsd)

       equations = []
       for p in points:
           ex = pol.subs(x, p[0])
           if nsd > 1:
               ex = ex.subs(y, p[1])
           if nsd > 2:
               ex = ex.subs(z, p[2])
           equations.append(ex)
           
       A = create_matrix(equations, coeffs)

       Ainv = A.inv()

       b = eye(len(equations))

       xx = Ainv*b

       for i in range(0,len(equations)):
           Ni = pol
           for j in range(0,len(coeffs)):
               Ni = Ni.subs(coeffs[j], xx[j,i])
           N.append(Ni)

       self.N = N