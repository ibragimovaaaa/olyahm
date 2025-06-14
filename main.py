from io import StringIO
import copy


class Node:
    def draw(self):
        buf = StringIO()
        for line in self._render("", True):
            buf.write(line + "\n")
        return buf.getvalue()

    def clone(self):
        return copy.deepcopy(self)

    def _render(self, prefix, is_last):
        raise NotImplementedError


class Cpu(Node):
    def __init__(self, cores, mhz):
        self.cores = cores
        self.mhz = mhz

    def _render(self, prefix, is_last):
        yield f"{prefix}{'\\-' if is_last else '+-'}CPU, {self.cores} cores @ {self.mhz}MHz"


class Memory(Node):
    def __init__(self, mib):
        self.mib = mib

    def _render(self, prefix, is_last):
        yield f"{prefix}{'\\-' if is_last else '+-'}Memory, {self.mib} MiB"


class Partition(Node):
    def __init__(self, index, gib, role):
        self.index = index
        self.gib = gib
        self.role = role

    def _render(self, prefix, is_last):
        yield f"{prefix}{'\\-' if is_last else '+-'}[{self.index}]: {self.gib} GiB, {self.role}"


class Disk(Node):
    def __init__(self, gib):
        self.gib = gib
        self.parts = []

    def add_part(self, part):
        self.parts.append(part)

    def _render(self, prefix, is_last):
        yield f"{prefix}{'\\-' if is_last else '+-'}HDD, {self.gib} GiB"
        sub = prefix + ("  " if is_last else "| ")
        for i, p in enumerate(self.parts):
            yield from p._render(sub, i == len(self.parts) - 1)


class Host(Node):
    def __init__(self, name):
        self.name = name
        self.addrs = []
        self.hw = []

    def add_addr(self, ip):
        self.addrs.append(ip)

    def add_hw(self, comp):
        self.hw.append(comp)

    def _render(self, prefix, is_last):
        yield f"{prefix}{'\\-' if is_last else '+-'}Host: {self.name}"
        sub = prefix + ("  " if is_last else "| ")
        total = len(self.addrs) + len(self.hw)
        for idx, ip in enumerate(self.addrs):
            last_here = idx == total - 1 and not self.hw
            yield f"{sub}{'\\-' if last_here else '+-'}{ip}"
        for jdx, comp in enumerate(self.hw):
            last = jdx == len(self.hw) - 1
            yield from comp._render(sub, last)


class Network(Node):
    def __init__(self, title):
        self.title = title
        self.hosts = []

    def add_host(self, h):
        self.hosts.append(h)

    def find_host(self, fqdn):
        for h in self.hosts:
            if h.name == fqdn:
                return h
        return None

    def _render(self, prefix, is_last):
        yield f"Network: {self.title}"
        for i, h in enumerate(self.hosts):
            yield from h._render("", i == len(self.hosts) - 1)


if __name__ == "__main__":
    net = Network("MISIS network")

    h1 = Host("server1.misis.ru")
    h1.add_addr("192.168.1.1")
    h1.add_hw(Cpu(4, 2500))
    h1.add_hw(Memory(16000))
    net.add_host(h1)

    h2 = Host("server2.misis.ru")
    h2.add_addr("10.0.0.1")
    h2.add_hw(Cpu(8, 3200))
    d = Disk(2000)
    d.add_part(Partition(0, 500, "system"))
    d.add_part(Partition(1, 1500, "data"))
    h2.add_hw(d)
    net.add_host(h2)

    print("=== draw сети ===")
    print(net.draw())

    print("=== поиск ===")
    found = net.find_host("server1.misis.ru")
    print(found.draw() if found else "None")

    print("=== clone ===")
    copy_net = net.clone()
    copy_net.hosts[0].name = "edited"
    print("оригинал:", net.hosts[0].name)
    print("копия   :", copy_net.hosts[0].name)
