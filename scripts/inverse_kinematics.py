import numpy as np

class Link():
    link_list = []

    def __init__(self, index: int, alpha, a, d, theta):
        self.index = index

        self.transformation_matrix = np.matrix([
            [np.cos(theta), -np.sin(theta) * np.cos(alpha), np.sin(theta) * np.sin(alpha), a * np.cos(theta)],
            [np.sin(theta), np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), a * np.sin(theta)],
            [0, np.sin(alpha), np.cos(alpha), d],
            [0, 0, 0, 1]
            ])
        
        print(f"Link {index}: \n{np.round(self.transformation_matrix, 2)}")
        
        Link.link_list.append(self)


def calculate_forward_kinematics(link_list: list[Link]):
    link_list.sort(reverse=False, key=lambda link: link.index)

    fk_matrix = np.identity(4)
    for link in link_list:
        print(f"Multiplying link {link.index}")
        fk_matrix = fk_matrix @ link.transformation_matrix

    return fk_matrix

thetas = [0, 0, 0, 0, 0]
L1 = 10
L2 = 10
L3 = 3


link1 = Link(1, 0, 0, 0, thetas[0])
link2 = Link(2, -(np.pi/2), 0, 0, thetas[1] - (np.pi/2))
link3 = Link(3, 0, L1, 0, thetas[2])
link4 = Link(4, 0, L2, -L3, thetas[3] + (np.pi/2))
link5 = Link(5, (np.pi/2), 0, 0, thetas[4])

fk_matrix = calculate_forward_kinematics(Link.link_list)

print("Final Matrix:")
print(np.round(fk_matrix, 2))

