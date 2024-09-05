class Node():
    """
    A node class for modelling a tree. It contains a name, its parent, a support count for usage in the FP tree, and a node it links to, if any
    """
    def __init__(self, name, parent = None):
        self.parent = parent #Set all the variables
        self.name = name
        self.count = 1 #Begin with a support count of 1
        self.children = [] #Create an empty list of children
        self.link = None #Say that it is currently not linked to any nodes
        if parent != None: #If there is a parent
            self.parent.children.append(self) #Append this child node to its parents list of child nodes
            
    def increment(self): #Add 1 to the counter of this node
        self.count += 1
        
    def get_node_string(self): #Return the name of the node and its current count
        if self.name != None:
            if self.link == None:
                return (self.name + " : " + str(self.count))
            else:
                return ("[]" + self.name + " : " + str(self.count))
        else:
            return "Null"
        
class DataSet():
    """
    A dataset class for handling data. Ideally, datasets should be a list of lists, with each sublists representing a string of transactions
    """
    def __init__(self, data):
        self.data = data
    
    def sort_items(self, support_threshold): #Create counts of the occurence of each individual item within the dataset
        support_threshold = support_threshold * len(self.data)
        print("Inputted dataset: ", self.data)
        #Creating a frequent pattern set based on support threshold
        self.items = {} #Create an empty dictionairy
        for transaction in self.data: #For every transaction in the dataset
            duplicates = [] #Create an empty list of found letters in the transaction
            for item in transaction: #For each item in the current transaction
                if item not in duplicates: #If it has not already been found
                    if item in self.items.keys(): #If the item has been found already
                        self.items[item] += 1 #Add one to its count
                    else: #Otherwise
                        self.items[item] = 1 #Add the item to the items dictionairy
                    duplicates.append(item) #Append the item to the duplicates dictionairy
        input()
        print("Counts of each item within the dataset: ", self.items)
        #Creating the ordered item set for each transaction
        unsupported_items = []
        for item, value in self.items.items():
            if value < support_threshold:
                unsupported_items.append(item)
        for item_to_del in unsupported_items:
            self.items.pop(item_to_del)
        self.item_counts = dict(sorted(self.items.items(), key=lambda item: item[1], reverse = True)) #Sort all found items by their respective counts in descending order
        input()
        print("Counts of each item that passed the support threshold of ", support_threshold, ":", self.item_counts)
        for i in range(len(self.data)): #Order each transaction based on the counts of each item
            self.data[i] = self.order_transaction(self.data[i])
        input()
        print("Ordered-item sets of each transaction: ", self.data)
        #Creating the frequent pattern tree
        self.construct_tree()
        print("The following FP tree is produced:")
        print_tree(self.root)
        #Constructing the conditional pattern base
        pattern_base = {}
        for item in reversed(self.item_counts.keys()): #For each item in ascending order
            item_patterns = []
            item_node = search_tree(item, self.root) #Search the tree for the first occurence of the item
            item_patterns.append((self.get_node_pattern(item_node.parent), item_node.count)) #Add the path to the item into the list of patterns
            while item_node.link != None:
                item_patterns.append((self.get_node_pattern(item_node.link.parent), item_node.link.count))
                item_node = item_node.link
            pattern_base[item] = item_patterns
        input()
        print("A conditional pattern base for each item is produced:")
        print(pattern_base)
        #Creating the conditional frequent pattern base for each item
        conditional_pattern_tree = {}
        for item, patterns in pattern_base.items(): #For each item
            conditional_pattern_tree[item] = self.create_cfp(patterns) #Create a conditional frequent pattern
        input()
        print("A conditional frequent pattern tree is then created:")
        print(conditional_pattern_tree)
        input()
        remove_keys = []
        for key in conditional_pattern_tree.keys(): #For each conditional pattern
            if conditional_pattern_tree[key][1] < support_threshold: #Check if it passes the support threshold
                remove_keys.append(key)
        for key_to_del in remove_keys:
            conditional_pattern_tree[key].pop()
        print("Patterns that have not passed the support threshold of ", support_threshold ," have been removed: ")
        print(conditional_pattern_tree)
        
    def create_cfp(self, patterns):
        finished = False
        iteration = 0 #Starting from 0
        most_common_pattern = [] #Begin with an empty list for the most common pattern
        while finished == False: #Whilst the most common pattern has not been found
            starting_patterns = [] #Create a list of the first parts of the patterns, up to the length of the iteration
            for pattern_tuple in patterns:
                current_start = []
                for i in range(iteration):
                    if i < len(pattern_tuple[0]):
                        current_start.append(pattern_tuple[0][i])
                    else:
                        finished = True
                starting_patterns.append(current_start)
            for start_index in range(len(starting_patterns)): #Compare all of the patterns, and mark that you have finished it they are not the same
                if (start_index + 1) != len(starting_patterns):
                    if starting_patterns[start_index] != starting_patterns[start_index + 1]:
                        finished = True
            iteration += 1 #Increase the iteration by 1
            if finished != True: #If you have not finished, copy the most common pattern and sum its frequency
                most_common_pattern = starting_patterns[0] 
                pattern_count = 0
                for pattern_tuple in patterns:
                    pattern_count += pattern_tuple[1]
        return (most_common_pattern, pattern_count) #Return the most common pattern and its frequency
    
    def order_transaction(self, transaction):
        new_transaction = []
        for item in self.item_counts.keys(): #For every item in the item list
            if transaction.count(item) != 0: #If the item is present in the list
                new_transaction.append(item) #Append it to the new list
        return new_transaction #Set the newly ordered list to the current transaction
        
    def construct_tree(self):
        self.root = Node(None) #Create a root node
        for transaction in self.data: #For each transaction in the dataset
            self.apply_tree_transaction(transaction, self.root) #Add each transaction to the tree, using the newly created root
            
    def apply_tree_transaction(self, transaction, cur_node):
        for item in transaction: #For each item in the transaction
            new_node_check = True #Mark that a new node should be created
            children = cur_node.children #Get the children of the current node
            for child in children: #Check if there is a child that matches the current item
                if child.name == item:
                    cur_node = child #Set the current node as the child
                    cur_node.increment() #Increment the support count of the matching child by 1
                    new_node_check = False #Mark that a new node doesn't need to be created for the given item
            if new_node_check: #If a new node needs to be created
                link_check = search_tree(item, self.root) #Check if the item is already in the tree
                new_node = Node(item, parent = cur_node) #Create a new node using the current node as a parent
                if link_check != False: #If the item is within the tree
                    while link_check.link != None: #Traverse until you reach the end of the links
                        link_check = link_check.link
                    link_check.link = new_node #Set the last occurence of the item to be linked to this new node
                cur_node = new_node #Set the current node to be the new node
                
    def get_node_pattern(self, node):
        pattern = [] #Create an empty list
        while node.parent != None: #Whilst the node still has a parent
            pattern.append(node.name) #Append the name of the node
            node = node.parent #Move to the parent of the node
        pattern.reverse() #Reverse the list
        return pattern
                
def search_tree(item, node):
    if node.name == item: #If the child has been found
        return node
    elif len(node.children) != 0:
        child_result = False
        for child in node.children:
            if search_tree(item, child) != False and child_result == False:
                child_result = search_tree(item, child)
        return child_result
    else:
        return False
    
def print_tree(root_node, spacing = 0): #Print a tree using the root_node argument as the root
    print(("  " * spacing) + "--" + root_node.get_node_string()) #Print the nodes information
    if len(root_node.children) > 0: #If there are any children
        for child in root_node.children: #Print them
            print_tree(child, spacing + 1) #With an extra layer of padding

raw_data = [["E", "K", "M", "N", "O", "Y"],
            ["D","E","K","N","O","Y"],
            ["A","E","K","M"],
            ["C","K","M","U","Y"],
            ["C","E","I","K","O","O"]
            ]
dataset = DataSet(raw_data)
dataset.sort_items(0.5)