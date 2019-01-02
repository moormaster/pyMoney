# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
def read(filename):
        with open(filename, 'r') as f:
                line = f.readline()

        version = []
        versionTokens = line.split(".")

        for t in versionTokens:
            version.append(int(t))

        return version


def write(filename):
        with open(filename, 'w') as f:
                f.write("2.0")
                f.close()
