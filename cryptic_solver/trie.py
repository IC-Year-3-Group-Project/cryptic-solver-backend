class Trie:

    # tree gives much better access and search time than a list

    def __init__(self):
        self.child_map = {}
        self.valid = False

    def print_all(self):
        builder = ""
        self.print_rec(builder)

    def print_rec(self, builder):
        if self.valid:
            print(builder)
        for key in self.child_map.keys():
            child = self.child_map.get(key)
            builder += key
            child.print_rec(builder)
            builder = builder[:-1]
        return


    def add(self, word):
        if len(word) == 0:
            self.valid = True
            return
        child = self.child_map.get(word[0])
        if child == None:
            child = Trie()
        child.add(word[1:])
        self.child_map.update({word[0]: child})        
        

    def search_rec(self, pattern, builder, results):
        if len(pattern) == 0:
            if self.valid:
                results.append(builder)
            return
        else:
            if pattern[0] == '_':
                for key in self.child_map.keys():
                    child = self.child_map.get(key)
                    builder += key
                    child.search_rec(pattern[1:], builder, results)
                    builder = builder[:-1]                   
            else:
                if pattern[0] in self.child_map:
                    builder += pattern[0]
                    self.child_map.get(pattern[0]).search_rec(pattern[1:], builder, results)
                    builder = builder[:-1]
                else:
                    return

    def search(self, pattern):
        builder = ""
        results = []
        self.search_rec(pattern, builder, results)
        return results




