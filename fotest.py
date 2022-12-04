string='本案在执行过程中，本院已采取如下执行措施或执行行为：'
stepflag=['申请执行人','被执行人','法定代表人','负责人','统一信用社']
for i in stepflag:
    if not i in string:
        print(1)