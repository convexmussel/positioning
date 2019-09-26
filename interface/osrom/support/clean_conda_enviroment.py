out = []
enviroment_name = "pyosrom"

with open("conda_enviroment.yml", "r+") as file:
    for line in file:
        if line.startswith("name:"):
            line = "name: " + enviroment_name + "\n"
        if line.startswith("prefix:"):
            line = ""
        out.append(line)
with open("conda_enviroment.yml", "w") as file:
    file.writelines(out)


