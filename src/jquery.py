class Query():

    def __init__(self,data):
        self.data = data

    def __build_query(self,q,condition,string_operator,sub_q=None):
        if string_operator:
            if sub_q:
                query = f'''if "{str(condition[2])}" {condition[1]} [str(x) for x in {str(sub_q[str(condition[0])])}]:
                                self.out.append(q)'''
            else:
                query = f'''if "{str(condition[2])}" {condition[1]} [str(x) for x in {str(q[str(condition[0])])}]:
                                self.out.append(q)'''    
        else:
            if sub_q:
                if str(sub_q[str(condition[0])]).isdigit():
                    query = f'''if {str(sub_q[str(condition[0])])} {condition[1]} {str(condition[2])}:
                                    self.out.append(q)'''
                else:
                    query = f'''if "{str(sub_q[str(condition[0])])}" {condition[1]} "{str(condition[2])}":
                                    self.out.append(q)'''
            else:
                if str(q[str(condition[0])]).isdigit():
                    query = f'''if {str(q[str(condition[0])])} {condition[1]} {str(condition[2])}:
                                    self.out.append(q)'''
                else:
                    query = f'''if "{str(q[str(condition[0])])}" {condition[1]} "{str(condition[2])}":
                                    self.out.append(q)'''  
        return query

    def __subQuery(self,q,condition):
        return q[condition]
    

    def where(self,condition):
        self.out = []
        condition = condition.split(" ")
        string_operator = False
        if condition[1] in ["in"]:
            condition[0],condition[2] = condition[2],condition[0]
            string_operator = True
        condition_pos_0 = condition[0].split(".")
        _list = False
        if "*" in condition_pos_0:
            _list = True
        for q in self.data:
            _subQ_para = condition[0].split(".")
            if len(_subQ_para) > 1:
                _q = q
                for i in _subQ_para[:-1]:
                    try:
                        sub_q = self.__subQuery(_q,i)
                        _q = sub_q
                    except:
                        pass
                sub_condition = [_subQ_para[-1]]+condition[1:]
                if isinstance(sub_q,list) and _list == True:
                    for _sub_q in sub_q:
                        try:
                            exec(self.__build_query(q=q,sub_q=_sub_q,condition=sub_condition,string_operator=string_operator))
                        except:
                            pass
                else:
                    try:
                        exec(self.__build_query(q=q,sub_q=sub_q,condition=sub_condition,string_operator=string_operator))
                    except:
                        pass
            else:
                try:
                    exec(self.__build_query(q=q,condition=condition,string_operator=string_operator))
                except: 
                    pass
        return Query(self.out)
    
    def get(self,key):
        de = []
        for d in self.data:
            de.append(d[key])
        return de

    def tolist(self,limit=None):
        if isinstance(limit, int):
            return self.data[:limit]
        return self.data
    