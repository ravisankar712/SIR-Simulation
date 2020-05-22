# SIR-Simulation
Simulation of the SIR model of epidemics, inspired from 3b1b video. Animations in pygame

Notation::
Blue dots :: Susceptible Individuals
Red Dots :: Infected
Yellow :: Indected with no symptoms
White :: Recovered

The main.py file has the following parameters,
pop size - Number of individuals
compartments - Number of districts (say). Individuals travel from district to district
initial infected
infection prob - probability of getting an infection, if a susceptible individual go near a infected one
perception radius - the radius around which each individual can ''see'' and interact with others
recovery time- number of frames after which an infected dot become recovered
syptom time - this is the time after which infected dot starts showing any symptoms
interstate travel prob - the prob of a dot traveling to another compartment
quarantine facility - if true, infected dots with symptoms (red) are taken to a zone with no contact to others
prob of symptoms - prob of an individual show any symptom at all. If an individual doesnt show symptm even after infected, it wont be quarantined

social distance start - the number of patients after which social distncing start. It is implemented as a repulsive force
percentage obeying social distance - the percent of people actually do social distancing
quarantine starts at - the number of patients after which quarantine start.
airport shut - the number of patients after which inter compartment travel stops.
dynamical rule change - if true, once the number of cases go down above given numbers, the social distancing, quarantine, shuttin air port etc are stopped again accordigly and if the numbers rise again, it starts again and so on.

Play with these!!
