import enum

class CellType(enum.Enum):
    gopher = 0 #our agent!
    door = 1 #entry point for agent into the trap
    wire = 2 #line that carries electrical pulses from entrance
    arrow = 3 #where projectile is shot from
    dirt = 4 #spaces between traps
    food = 5 #contains food for gopher
    floor = 6 #empty space in a trap