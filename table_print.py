# users = [
#         {
#             "name": "Codeforces Round 1074 (Div. 4)",
#             "phase" : "FINISHED"
#         },
#         {
#             "problems" : ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
#         },
#         {
#             "handle" : "jnbl",
#             "rank" : " (1)",
#             "points" : ["1","1","1","1","1","1","1","1", ""], #8
#         },
#         {
#             "handle" : "* Xjanbol",
#             "rank" : " ",
#             "points" : ["1","1","+3","1","1","-4","0","+1", "0"], #8
#         }
#     ]

class PrettyTable:
    def __init__(self, users_data):
        self.users = users_data
    @staticmethod
    def prettyTable(problems, users):
        #determine the borders length 
        mx_length = len(problems[0])
        
        divider = "+"
        for i in range(mx_length):
            divider+="-----+" #5 dashes + 1 plus

        result = ""

        #Problems
        result +=divider+'\n'
        for i in problems:
            for j in i:
                result += j
            result += "|\n"
        result += divider + '\n'

        #Users
        for user in users:
            #result += f"|{"":^{mx_length*6-1}}|" + '\n' - this is top padding 
            user_name_rank = f"|{user["handle"]+user["rank"]:^{mx_length*6-1}}|"
            result += user_name_rank + '\n'
            for i in user["problems"]:
                for j in i:
                    result += j
                result += "|\n"
            result += divider + '\n'

        return result
    @staticmethod
    def rows(lst):
        main_list =[]
        i = 0

        tmp_lst = []
        for l in lst:
            if i % 7==0:
                if i != 0:
                    main_list.append(tmp_lst)
                tmp_lst = [f"|{l:^{5}}"]
            else:
                tmp_lst.append(f"|{l:^{5}}")
            i+=1

        if len(lst)>7:
            while len(tmp_lst) < 7:
                tmp_lst.append(f"|{"":{5}}")

        main_list.append(tmp_lst)
        
        return main_list

    def generate_table(self):
        
        users_data = []
        for user in self.users[2:]:
            problems = self.rows(user["points"])
            users_data.append(
                {
                    "handle" : user["handle"],
                    "rank" : user["rank"],
                    "problems" : problems
                }
            )

        problems = self.rows(self.users[1]["problems"])

        table = self.prettyTable(problems, users_data)

        return table

    