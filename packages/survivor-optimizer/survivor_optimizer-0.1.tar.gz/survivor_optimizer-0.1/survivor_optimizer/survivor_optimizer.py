
import numpy as np

class Survivor:
    def __init__(self, problem, nvar, xmin, xmax, params, SF=1, LF=5):
        self.problem = problem
        self.nvar = nvar
        self.xmin = xmin
        self.xmax = xmax
        self.npop = params['npop']
        self.itermax = params['itermax']
        self.wdamp = params.get('wdamp', 0.99)
        self.SF = SF
        self.LF = LF

        self.EFN = 0
        self.Curv_best_global = np.zeros(self.itermax)
        self.Curv_best_local = np.zeros(self.itermax)
        self.w = 2
        self.ArchiveSize = 10
        self.Archive = []
        self.swarm = self.initialize_swarm()
        self.globest = {'loc': self.swarm[0]['loc'].copy(), 'cost': self.swarm[0]['cost']}

    def initialize_swarm(self):
        swarm = []
        for i in range(self.npop):
            loc = np.random.uniform(self.xmin, self.xmax, self.nvar)
            cost = self.problem(loc)
            self.EFN += 1
            member = {
                'loc': loc,
                'dis': np.zeros(self.nvar),
                'Ploc': np.zeros(self.nvar),
                'Bloc': loc.copy(),
                'Bloc1': loc.copy(),
                'Bloc2': loc.copy(),
                'Bcos': cost,
                'cost': cost,
                'S': 0.5,
                'L': 0.5,
                'N': 1 if i < self.npop//2 else 2,
                'LCount': 0,
                'LossCountG': 2,
                'best': {'loc': loc.copy(), 'cost': cost}
            }
            swarm.append(member)
        for i in range(self.npop//2):
            swarm[i]['Ploc'] = swarm[i+self.npop//2]['loc'].copy()
            swarm[i+self.npop//2]['Ploc'] = swarm[i]['loc'].copy()
        return swarm

    def update_swarm(self):
        F = np.full(self.npop, 0.08)
        bestcost = np.zeros(self.itermax)

        for iter in range(self.itermax):
            for i, member in enumerate(self.swarm):
                F[i] = F[i] + 0.1*(np.random.rand() - F[i])
                contestant = member['cost']
                opponent = self.problem(member['Ploc'])
                mean_cost = np.mean([m['cost'] for m in self.swarm])

                if (contestant < mean_cost) and (self.SF in [1,2]):
                    SF = self.SF
                else:
                    SF = np.random.randint(1,3)

                if SF == 1:
                    member['loc'] += np.random.rand()*(self.globest['loc']-member['loc'])                                      + np.random.rand()*(member['Bloc']-member['loc'])
                    if len(self.Archive) > 0:
                        rand_idx = np.random.randint(len(self.Archive))
                        member['loc'] += F[i]*(member['loc'] - self.Archive[rand_idx])
                    member['loc'] = np.clip(member['loc'], self.xmin, self.xmax)
                else:
                    member['dis'] = member['L']*member['dis']
                    member['dis'] = self.w*member['dis'] + member['S']*np.random.rand(self.nvar) *                                     ((member['Bloc'] + self.globest['loc'])/np.sqrt(F[i]*member['LossCountG']) - member['loc'])
                    member['loc'] = np.clip(member['loc'] + member['dis'], self.xmin, self.xmax)

                member['cost'] = self.problem(member['loc'])
                self.EFN += 1

                if member['cost'] < member['Bcos']:
                    member['Bloc'] = member['loc'].copy()
                    member['Bcos'] = member['cost']
                    self.Archive.append(member['loc'].copy())
                    if len(self.Archive) > self.ArchiveSize:
                        self.Archive.pop(0)

                if member['cost'] < self.globest['cost']:
                    self.globest['loc'] = member['loc'].copy()
                    self.globest['cost'] = member['cost']

            bestcost[iter] = self.globest['cost']
            if (iter+1) % 50 == 0:
                print(f"Survivor {iter+1}: {self.globest['cost']:.6f}")
            self.w *= self.wdamp

        self.Curv_best_global = bestcost.copy()
        self.Curv_best_local = bestcost.copy()

        return self.EFN, self.globest['cost'], self.globest['loc'], self.Curv_best_local, self.Curv_best_global
