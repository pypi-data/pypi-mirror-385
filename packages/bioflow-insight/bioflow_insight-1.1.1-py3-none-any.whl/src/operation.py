

import warnings

#TODO
#- uniform eveything here
#- add a list of words illegal for channel eg. [true, process, workflow...]

import re
from .outils import get_end_operator, get_end_call, get_curly_count, operation_2_DSL2
from .code_ import Code
from .condition import Condition
from .executor import Executor
from .bioflowinsighterror import BioFlowInsightError
from . import constant


class Operation(Executor):
    def __init__(self, code, origin, OG_code = ''):
        self.origin = origin
        self.code = Code(code, origin = self, initialise=False)
        self.origins = []
        self.gives = []
        self.label = ""
        self.calls = {}
        self.OG_code = OG_code
        self.show_in_structure = True
        self.operation_type = None
        #Artificial means that it is created by the analysis -> it is not native in the code
        self.artificial = False
        self.create_loop_with_call = False
        #It's important this is last
        #self.condition = Condition(self)

    def change_code(self, code):
        self.OG_code = self.get_code()
        self.code = Code(code, origin = self, initialise=False)

    def set_as_artificial(self):
        self.artificial = True
    
    def get_artificial_status(self):
        return self.artificial


    def get_create_loop_with_call_status(self):
        return self.create_loop_with_call

    def add_element_gives(self, ele):
        self.gives.append(ele)

    def add_element_origins(self, ele):
        self.origins.append(ele)


    def is_defined_in_process(self, process):
        if(len(self.gives)!=0):
            raise Exception(f"This operation is defined in {process.get_name()} shoudn't be able to give a channel")
        #Don't need to remove it from the list of operations cause it was never added (that's done outside of the operation)
        for c in self.origins:
            c.remove_element_from_sink(self)
            c.add_sink(process)

    def get_name(self):
        return str(self)

    
    def get_gives(self):
        return self.gives
    
    def get_type(self):
        return "Operation"
    
    #def check_in_channels(self, channel):
    #    return self.origin.check_in_channels(channel)   

    #def add_channel(self, channel):
    #    self.origin.add_channel(channel)   

    def get_elements_called(self, tab = []):
        for o in self.origins:
            if(o.get_type()=="Call"):
                tab+=o.get_elements_called()
        return tab

    #def add_origin_channel(self, name):
    #    from .channel import Channel
    #    #Check that the name is not the list of illegal words
    #    #and Check that the thing extarcted is not WorkflowNameFile like 'WorkflowHgtseq' in nf-core/hgtseq
    #    if(name not in constant.ERROR_WORDS_ORIGINS):# and name.lower()!=f"workflow{self.get_name_file().lower()}"):
    #        #channel = Channel(name=name, origin=self.origin)
    #        if(self.origin.get_type()!="Subworkflow"):
    #            #First check that the channel is not defined at the same level
    #            channels = self.origin.get_channels_from_name_same_level(name)
    #            #Then check that the channel is defined in the below level
    #            if(channels==[]):
    #                channels = self.origin.get_channels_from_name_inside_level(name)
    #            #Finally check if the channels is defined above
    #            if(channels==[]):
    #                channels = self.origin.get_channels_from_name_above_level(name)
    #            if(channels==[]):
    #                channels = self.origin.get_channels_from_name_other_blocks_on_same_level(name)
    #            #If it still doesn't exist -> we create it 
    #            if(channels==[]):
    #                channel = Channel(name=name, origin=self.origin)
    #                self.origin.add_channel(channel)
    #                channels = [channel]
    #        else:
    #            channel = Channel(name=name, origin=self.origin)
    #            self.origin.takes_channels.append(channel)
    #            channels = [channel]
    #        
    #        for channel in channels:
    #            self.origins.append(channel)
    #            #channel.initialise()
    #            channel.add_sink(self)



    def add_origin_channel(self, name):
        from .channel import Channel
        #Check that the name is not the list of illegal words
        #and Check that the thing extarcted is not WorkflowNameFile like 'WorkflowHgtseq' in nf-core/hgtseq
        if(name not in constant.ERROR_WORDS_ORIGINS):# and name.lower()!=f"workflow{self.get_name_file().lower()}"):
            #channel = Channel(name=name, origin=self.origin)
            if(self.origin.get_type()!="Subworkflow"):
                origin = self.origin
            else:
                origin = self.origin.root
            
            #V1
            #First check that the channel is not defined at the same level
            channels = origin.get_channels_from_name_same_level(name)
            #Then check that the channel is defined in the below level
            if(channels==[]):
                channels = origin.get_channels_from_name_inside_level(name)
            #Finally check if the channels is defined above
            if(channels==[]):
                channels = origin.get_channels_from_name_above_level(name)
            if(channels==[]):
                channels = origin.get_channels_from_name_other_blocks_on_same_level(name)

            #V2
            channels = origin.get_channels_from_name_same_level(name)+origin.get_channels_from_name_inside_level(name)+origin.get_channels_from_name_above_level(name)+origin.get_channels_from_name_other_blocks_on_same_level(name)
            channels = list(set(channels))
            
            #If it still doesn't exist -> we create it 
            if(channels==[]):
                channel = Channel(name=name, origin=origin)
                origin.add_channel(channel)
                channels = [channel]
            #else:
            #    print(name)
            #    channel = Channel(name=name, origin=self.origin)
            #    self.origin.takes_channels.append(channel)
            #    channels = [channel]
            
            for channel in channels:
                self.origins.append(channel)
                #channel.initialise()
                channel.add_sink(self)
        


    #I don't need to define the equivalent gives -> cause it's not possible:)
    def add_origin_emits(self, full_code, name_called, name_emitted):
        from .emitted import Emitted
        #Check that it not already been added
        added = False
        for o in self.origins:
            if(full_code==o.get_code()):
                added = True

        if(not added):
            #full_code, name_called, name_emitted = match.group(1), match.group(2), match.group(3)
            IGNORE_NAMES = ['params']
            #In the cas an operator is extracted at the end of the emit
            if(full_code.count('.')>=2):
                splited = full_code.split('.')
                if( splited[-1] in constant.LIST_OPERATORS):
                    full_code = '.'.join(splited[:-1])
            if(name_called not in IGNORE_NAMES):
                calls = self.get_calls_by_name(name_called)

                if(calls!=[]):
                    for call in calls:
                        #print(full_code, self.get_code(get_OG=True))
                        emitted = Emitted(name=full_code, origin=self.origin, emitted_by=call)
                        emitted.set_emits(name_emitted)
                        emitted.add_sink(self)
                        self.origins.append(emitted)
                else:
                    #if(self.get_cycle_status()):
                    #    raise BioFlowInsightError(f"A cycle (inderect or direct) exists in the workflow. The rewrite could not be done with the proprosed relavant processes. Either correct the defintion of the workflow or give another set of relevant processes.", type="Cycle exists in workflow")
                    if(name_called[:5]=="Call_"):
                        name_called = self.calls[name_called].get_code()
                    raise BioFlowInsightError("ccnbf", self, name_called, self.get_code(get_OG=True), self.get_string_line(self.get_code(get_OG=True)))
                    

                

    #This methods checks if the input is an emit and adds it if it's the case, it also returns T/F if it's an emit
    def check_is_emit(self, name):
        pattern_emit_tab = constant.EMIT_TAB
        pattern_emit_name = constant.EMIT_NAME
        patterns = [pattern_emit_tab, pattern_emit_name]
        found_an_emit = False
        for pattern in patterns:
            for match in re.finditer(pattern, name):
                found_an_emit = True
                full_code, name_called, name_emitted = match.group(0), match.group(1), match.group(3)
                if(name_emitted not in constant.LIST_OPERATORS):
                    self.add_origin_emits(full_code, name_called, name_emitted)
                else:
                    self.add_origin_emits(full_code, name_called, "")

        if(not found_an_emit):
            for match in re.finditer(constant.EMIT_ALONE, name+' '):
                found_an_emit = True
                full_code, name_called = match.group(0).strip(), match.group(1)
                self.add_origin_emits(full_code, name_called, "")

        return found_an_emit

    #Function that returns if an operation is a create or a branch
    def get_operation_type(self):
        if(self.operation_type==None):
            if(len(self.origins)!=0 and len(self.gives)!=0):
                return 'Branch'
            else:
                return 'Create'
        return self.operation_type
        
    def set_operation_type(self, type):
        self.operation_type = type


    #Here since the operation "gives" a channel -> we don't check 
    #if it's a global channel since we are defining a new one
    def add_gives(self, name):
        from .channel import Channel
        #Case it's a call and it's been replaced
        if(re.fullmatch(constant.CALL_ID, name)):
            self.add_element_gives(self.calls[name])
            raise Exception("This shoudn't happen! -> a call is taking a value")
        
        else:
            
            origin = None
            #Case the emited thing is an operation -> of type 'ch = existing_channel' 
            if(self.origin.get_type()=="Subworkflow"):
                origin = self.origin.root
            else:
                origin = self.origin
            
            #V1
            channels = origin.get_channels_from_name_same_level(name)
            if(channels==[]):
                channels = origin.get_channels_from_name_inside_level(name)
            if(channels==[]):
                channels = origin.get_channels_from_name_above_level(name)
            #if(channels==[]):
            #    channels = origin.get_channels_from_name_other_blocks_on_same_level(name)
            
            #V2
            #channels = origin.get_channels_from_name_same_level(name)+origin.get_channels_from_name_inside_level(name)+origin.get_channels_from_name_above_level(name)

            if(channels==[]):
                channel = Channel(name=name, origin=self.origin)
                origin.add_channel(channel)
                channels = [channel]

            for channel in channels:
                self.add_element_gives(channel)
                #channel.initialise()
                channel.add_source(self)

    def add_origin(self, name):
        name = name.strip()
        #Check that it's not already been added
        added = False
        for o in self.origins:
            if(name==o.get_code()):
                added = True

        if(not added):
            if(self.origin.get_DSL()=="DSL2"):
                #Case it's a call and it's been replaced
                if(re.fullmatch(constant.CALL_ID, name)):
                    self.origins.append(self.calls[name])
                else:
                    ##Case it's a subworkflow
                    #subworkflow = self.origin.get_subworkflow_from_name(name)
                    #process = self.origin.get_process_from_name(name)
                    #if(subworkflow!=None):
                    #    #Case suborkflow
                    #    self.origins.append(subworkflow)
                    ##Case process
                    #elif(process!=None):
                    #    #Case process
                    #    self.origins.append(process)
                    ##In this case it's a channel
                    #else:
                    self.add_origin_channel(name)
            else:
                self.add_origin_channel(name)
                

    #Function that from an operation gives the origin ('input') channels
    #For every case i have checked by compilying the nextflow code for each operator
    def initialise_origins(self):
        operation = self.get_code(clean_pipe = True)+" "
        ERROR_WORDS = constant.ERROR_WORDS_ORIGINS

        #Replace the channels written like "ch[0]" to "ch" -> since in anycase it's just a 
        #subpart of the channel (we can't analyse what's in the channel)
        replacing_tab = True
        while(replacing_tab):
            replacing_tab = False
            pattern_channel_tab = constant.CHANNEL_TAB
            for match in re.finditer(pattern_channel_tab, operation):
                if(match.group(1) not in ["out", "output"]):
                    operation = operation.replace(match.group(0), match.group(1))
                    replacing_tab = True
                    break

        #pattern= r'([^\=\n]+)\s*=\s*([^\?\n]+)\s*\?([^\n]+)'
        #if(bool(re.fullmatch(pattern, operation))):
        #     for match in re.finditer(pattern, operation):
        #          origin_temp = match.group(3).split(":")
        #          for o in origin_temp:
        #               origin.append(o.strip())
                    

        #else:
                
        #If the first word after an '=' is not the channel key word than it is an actual channel
        #TODO -> check if this condition actually works!!
        #temp = operation.split('.')[0].split('=')[-1].strip()
        #if(get_first_word(temp)!='Channel' and get_first_word(temp)!='channel'):
        #    origin.append(get_first_word(temp)) 

        #TODO -> does this case ever exist?
        #================================
        #Case channel1
        #================================
        if(bool(re.fullmatch(constant.WORD, operation.strip()))):
            self.add_origin(operation)


        #Case tupel with call -> this is not supported by BioFlow-Insight -> try calling first then using the emits
        if(bool(re.fullmatch(r"\( *\w+ *(\, *\w+)+ *\) *= *Call_\d+", operation.strip()))):
            line = self.get_string_line(self.get_code(get_OG= True))
            raise BioFlowInsightError("taws", self, "call", line)

        searching_for_emits = True
        while(searching_for_emits):
            searching_for_emits = False
            stop_pattern_search = False
            for pattern in [constant.EMIT_NAME, constant.EMIT_TAB, constant.EMIT_ALONE]:
                for match in re.finditer(pattern, operation+" "):
                    try:
                        full_code, name_called, name_emitted = match.group(0), match.group(1), match.group(3)
                    except:
                        full_code, name_called, name_emitted = match.group(0)[:-1], match.group(1), ""
                    if(name_emitted==""):
                        self.add_origin_emits(full_code, name_called, "")
                    if(name_emitted in constant.LIST_OPERATORS):
                        pos = self.get_code().find(full_code)
                        #This basically checks if the name_emitted is an operation or not
                        if(pos+len(full_code)>=len(self.get_code())
                           or self.get_code()[pos+len(full_code):].strip()[0] not in ["(", "{"]):
                            #Case not an operation
                            self.add_origin_emits(full_code, name_called, name_emitted)
                        else:
                            #Case Operation
                            full_code = '.'.join(full_code.split(".")[:-1])
                            self.add_origin_emits(full_code, name_called, "")
                    else:
                        self.add_origin_emits(full_code, name_called, name_emitted)
                    temp = operation
                    operation = operation.replace(full_code, "")
                    if(temp==operation):
                        raise Exception("This souldn't happen")
                    searching_for_emits = True
                    stop_pattern_search = True
                    break
                if(stop_pattern_search):
                    break


        case_operation_starts_with_emit = False
        #---------------------------
        #Check emits
        #---------------------------
        #================================
        #Case call.out[num]
        #================================
        #TODO -> here i assume that the [] is a decimal not necessary the case
        pattern_emit_tab = constant.EMIT_TAB
        #================================
        #Case channel1 = call.out.something
        #================================
        pattern_emit_name = constant.EMIT_NAME
        patterns = [pattern_emit_tab, pattern_emit_name]

        for pattern in patterns+[r"\w+"]:
            #Replace the emits and channels around parenthese by just themselves (without the parantheses)
            def replace(text):
                def replacer(match):
                    return match.group(0).replace(match.group(1), match.group(2))
                return re.sub(fr"[^\w\s] *(\(\s*({pattern})\s*\))", replacer, text)
        
            operation = replace(operation)

        first_call = True
        for pattern in patterns:

            #================================
            #Case channel1 = emits
            #================================
            pattern_equals = r"\w+\s*=\s*\(?\s*("+pattern+r")"
            for match in re.finditer(pattern_equals, operation):
                full_code, name_called, name_emitted = match.group(1), match.group(2), match.group(4)
                if(name_emitted in constant.LIST_OPERATORS):
                    self.add_origin_emits(full_code, name_called, "")
                else:
                    self.add_origin_emits(full_code, name_called, name_emitted)
                case_operation_starts_with_emit = True
        
            #================================
            #Case call.out[].something().. or call.out.channel.something().. -> we want to extract that emits
            #================================
            for match in re.finditer(pattern, operation):
                if(first_call):
                    full_code, name_called, name_emitted = match.group(0), match.group(1), match.group(3)
                    
                    #Check that it's a the begining of the operation
                    code = operation
                    operation_until_out = code[:code.find("out")]
                    if(operation_until_out==full_code[:full_code.find("out")]):
                        code_wo_spaces = code.replace(' ', '')
                        #We check that the term after the out is an operator or a channel
                        is_operator = True
                        try:
                            if(code_wo_spaces[len(match.group(0).replace(' ', ''))] in ['(', '{']):
                                is_operator=True
                            else:
                                is_operator=False
                        except:
                            is_operator=False
                        if(is_operator):
                            self.add_origin_emits(full_code, name_called, "")
                        else:
                            self.add_origin_emits(full_code, name_called, name_emitted)
                        case_operation_starts_with_emit = True
                    first_call = False

       
        #Here i the case where we assume the emit looks like "call.out"
        if(not case_operation_starts_with_emit):
            #================================
            #Case channel1 = emits
            #================================
            pattern_equals = constant.EMIT_EQUALS
            for match in re.finditer(pattern_equals, operation):
                full_code, name_called = match.group(1), match.group(2)
                self.add_origin_emits(full_code, name_called, "")
                case_operation_starts_with_emit = True

            #================================
            #Case call.out.something().. we want to extract that emits
            #================================
            #for match in re.finditer(r"(\w+)\s*\.\s*out", operation):
            #TODO -> check this 
            #I've changed this to avoid problems like this : "ch_svdb_dbs.out_occs.toList()"
            for match in re.finditer(constant.EMIT_OPERATION, operation+" "):
                    #full_code, name_called = match.group(1), match.group(2)
                    #self.add_origin_emits(full_code, name_called, "")
                    ##Remove the emit from the operation code -> so we don't extract it agian
                    #operation = operation.replace(full_code, "")
                    
                    #Old
                    full_code, name_called = match.group(1), match.group(2)
                    #Check that it's a the begining of the operation
                    operation_until_out = operation[:operation.find("out")]
                    if(operation_until_out==full_code[:full_code.find("out")]):
                        self.add_origin_emits(full_code, name_called, "")
                        case_operation_starts_with_emit = True
                        temp = operation
                        operation = operation.replace(full_code, "")
                        if(temp==operation):
                            raise Exception("This souldn't happen")



        if(not case_operation_starts_with_emit):
            #================================
            #Case channel1 = channel2.something
            #================================
            pattern= constant.CHANNEL_EQUALS_OPERATION
            for match in re.finditer(pattern, operation):
                if(match.group(1) not in ERROR_WORDS):
                    #Here we create the channel from the name -> checks if it already exists in the workflow
                    name = match.group(1)
                    if(bool(re.fullmatch(constant.WORD, name))):
                        self.add_origin(name)

            #================================
            #Case channel1 = [.., ..]
            #================================
            pattern= constant.CHANNEL_EQUALS_LIST
            if(bool(re.fullmatch(pattern, operation.strip()))):
                for match in re.finditer(pattern, operation):
                    origin_possibilities = match.group(1).split(",")
                    for o in origin_possibilities:
                        name = o.strip()
                        if(name not in ERROR_WORDS):
                            #Here we create the channel from the name -> checks if it already exists in the workflow
                            if(bool(re.fullmatch(constant.WORD, name))):
                                self.add_origin(name)

            #================================
            #Case (ch1, ch2, ...) = emit.out
            #================================
            pattern= constant.TUPLE_EMIT
            for match in re.finditer(pattern, operation):
                raise BioFlowInsightError("taws", self, "emit", self.get_string_line(self.get_code(clean_pipe = False)))



            #================================
            #Case (ch1, ch2, ...) = channel.something
            #================================
            pattern= constant.TUPLE_EQUALS
            for match in re.finditer(pattern, operation):
                if(match.group(2) not in ERROR_WORDS):
                    #Here we create the channel from the name -> checks if it already exists in the workflow
                    name = match.group(2)
                    if(bool(re.fullmatch(constant.WORD, name))):
                        self.add_origin(name)
            
            #================================
            #Case channel1 = channel2
            #================================
            if(bool(re.fullmatch(constant.CHANNEL_EQUALS, operation.strip()))):
                temp = operation.split('=')[-1].strip()
                if(temp not in ERROR_WORDS and bool(re.fullmatch(constant.WORD, temp))):
                    #Here we create the channel from the name -> checks if it already exists in the workflow
                    self.add_origin(temp)


            #================================
            #Case (ch1, ch2, ...) = (ch1_1, ch2_1, ...)
            #================================
            #Nextflow doesn't allow this 
            #TODO -> double check

            #================================
            #Case channel.something().. -> we want to extract that channel
            #================================
            index_dot = operation.find(".")
            if(index_dot!=-1):
                if(bool(re.fullmatch(constant.WORD_DOT, operation[:index_dot+1].strip()))):
                    temp = operation[:index_dot].strip()
                    if(temp not in ERROR_WORDS and bool(re.fullmatch(constant.WORD, temp))):
                        #Here we create the channel from the name -> checks if it already exists in the workflow
                        name = temp
                        if(bool(re.fullmatch(constant.WORD, name))):
                            self.add_origin(name)

       

        #================================
        #merge/ mix/ concat/ spread/ join/ phase/ cross/ combine
        #================================
        pattern= constant.MERGE_OPERATIONS
        for match in re.finditer(pattern, operation):
            start, end, beginning_character= match.span(1)[0], match.span(1)[1], match.group(3)
            operator_call, operator_params = get_end_operator(operation, start, end, beginning_character)
            spliting_param = ''
            if(beginning_character=="("):
                spliting_param=","
            if(beginning_character=="{"):
                spliting_param=";"
            temp= operator_params.split(spliting_param)
            for t in temp:
                name = t.strip()
                #Case channel
                if(bool(re.fullmatch(constant.WORD, name))):
                    self.add_origin(name)
                else:
                    #check and add if it's an emitted value
                    emited = self.check_is_emit(name)
                    if(not emited):
                        #TODO -> check at what extend this is used
                        #This is just a trick so i don't have to specifically define the methods for subworkflows
                        thing = self
                        if(self.origin.get_type()=="Subworkflow"):
                            thing = self.origin.root
                        channels = thing.get_channels_same_level()+thing.get_channels_above_level()+thing.get_channels_inside_level()+thing.get_channels_from_other_blocks_on_same_level()
                        for c in channels:
                            if(c.get_name() in name):
                                pos = [m.start() for m in re.finditer(c.get_name(), operation)]
                                to_add = True
                                for p in pos:
                                    if(p>0):
                                        #Check it is actually the channel and not a different channel
                                        if(bool(re.fullmatch(constant.ILLEGAL_CHARCTER_BEFORE_POTENTIAL_CHANNELS, operation[p-1]))):
                                            to_add = False
                                        if(bool(re.fullmatch(constant.ILLEGAL_CHARCTER_AFTER_POTENTIAL_CHANNELS, operation[p+len(c.get_name())]))):
                                            to_add = False
                                if(to_add):
                                    self.add_origin(c.get_name())
                        #TODO update this -> it's an operation itselfs
                        #warnings.warn(f"I don't know what i'm looking at '{name}' in '{self.get_code()}'\n")




    #Method that intialises the gives (the outputs) of an opeartion
    def initialise_gives(self):
        code = self.get_code(clean_pipe = True)
        #Case channel1 = something -> then channel1 is added to the gives
        if(bool(re.fullmatch(constant.CHANNEL_EQUALS_SOMETHING, code))):
            first_gives = code.split("=")[0].strip()
            if(bool(re.fullmatch(constant.WORD, first_gives))):
                self.add_gives(first_gives)
        
        #Case (ch1, ch2, ...) = something -> then ch1, ch2, ... is added to the gives
        elif(bool(re.fullmatch(constant.TUPLE_EQUALS_SOMETHING, code))):
            for match in re.finditer(constant.TUPLE_EQUALS_SOMETHING, code):
                to_give = match.group(1)[1:-1]#Removing the parentheses
                to_give = to_give.split(",")
                for g in to_give:
                    g = g.strip()
                    if(bool(re.fullmatch(constant.WORD, g))):
                        self.add_gives(g)
                    else:
                        raise Exception("Something unexpected")

        #else:
        #    raise Exception("Something unexpected!")
                
       
        #Cases we use the "set" operators
        set_operators = constant.SET_OPERATORS
        start_end = [["(", ")"], ["{", "}"]]
        for operator in set_operators:
            for start, end in start_end:
                pattern = f"{operator}\s*\{start}([^\{end}]+)\{end}"
                for match in re.finditer(pattern, code):
                    channels = match.group(1)
                    #Add channel
                    gives = re.split(';|,|\n', channels)
                    for g in gives:
                        c = g.strip()
                        if(c!=""):
                            if(bool(re.fullmatch(constant.WORD, c))):
                                if(not bool(re.fullmatch(constant.NUMBER, c))):
                                    self.add_gives(c)
                            else:
                                #check and add if it's an emitted value
                                emited = self.check_is_emit(c)
                                #TODO -> do i not need to add it in the gives?
                                if(not emited):
                                    raise Exception(f"I don't know what i'm looking at '{c}' in '{self.get_code()}'")
                            
                    
    
    

    def get_origins(self):
        return self.origins
    
    #def get_origins(self):
    #    tab = []
    #    for o in self.origins:
    #        #tab.append(o.get_name())
    #        tab.append(o)
    #    return tab

    def get_gives(self):
        tab = []
        for g in self.gives:
            #tab.append(g.get_name())
            tab.append(g)
        return tab
    


    #This method checks if an operation is just a full emited 
    #This is in the case of a parameter in a call
    def check_if_operation_is_an_full_emitted(self):
        #george_here
        pattern_emit_tab  = constant.EMIT_TAB
        pattern_emit_name = constant.EMIT_NAME
        pattern_emit_full = constant.EMIT_ALONE_2
        patterns = [pattern_emit_tab, pattern_emit_name, pattern_emit_full]
        for pattern in patterns:
            if(bool(re.fullmatch(pattern, self.get_code(clean_pipe = True)))):
                return True
        return False

    

    def write_summary(self, address, tab = 0):
        file = open(address, "a") 
        file.write("  "*tab+f"{self}\n") 
        file.write("  "*(tab+1)+"* Code : "+str(self.get_code(get_OG=True))+ "\n")
        file.write("  "*(tab+1)+"* Origins"+ "\n")
        for o in self.get_origins():
            file.write("  "*(tab+1+2)+o.get_code()+ f" '{o.get_type()}'\n")
        file.write("  "*(tab+1)+"* Gives\n")
        for g in self.get_gives():
            file.write("  "*(tab+1+2)+g.get_code()+ f" '{g.get_type()}'\n")
        
        file.write("\n")
        
        # Closing the opened file 
        file.close()


    def get_code(self, replace_calls = True, clean_pipe = False, get_OG=False, remove_emit_and_take = False):
        #exe.get_code(remove_emit_and_take = True, replace_calls = False)
        code = self.code.get_code()
        if(get_OG):
            if(self.OG_code!=""):
                code = self.OG_code
            if(code[:3] in ["e: ", "t: "] and self.get_artificial_status()):
                #print("-", code)
                code = code[3:]
                code = code.strip()
            return code
            
        if(clean_pipe):
            code, self.dico_OG_call_2_new_call = self.clean_pipe_operator(code)
  
        if(replace_calls):
            for call in self.calls:
                temp = code
                code = code.replace(self.calls[call].get_code(), str(call))
                if(temp==code):
                    raise Exception("This souldn't happen")
        
        #Remove "e:" and "t:" for the subworkklfow inputs and outputs
        if(remove_emit_and_take and code[:3] in ["e: ", "t: "] and self.get_artificial_status()):
            #print("-", code)
            code = code[3:]
            code = code.strip()
            
            
        return code
    
    def initialise_double_dot(self):
        self.extract_calls(clean_pipe=False)
        code = self.get_code(clean_pipe = False)
        pattern = constant.DOUBLE_DOT
        for match in re.finditer(pattern, code):
            double_dot = match.group(0).strip()
        
            c = double_dot.split("=")[0].strip()
            self.add_gives(c)
            
            possibilities = double_dot[double_dot.rfind('?')+1:].split(":")
            for p in possibilities:
                p = p.strip()
                if(p!=""):
                    name = p
                    if(bool(re.fullmatch(constant.WORD, name))):
                        self.add_origin(name)
                    elif(self.check_is_emit(name)):
                        None
                    #else:
                    #    raise Exception(f"Don't know what i'm looking at '{name}' in operation '{self.get_code()}', in file '{self.get_file_address()}'!")
                

    

    def extract_calls(self, clean_pipe = True):
        from .call import Call
        to_call = []
        for m in self.get_modules_defined():
            to_call.append(m.get_alias())
        pattern_call = constant.BEGINNING_CALL
        searching = True        
        while(searching):
            searching= False
            text = " "+self.get_code(clean_pipe = clean_pipe, replace_calls = False)
            for c in self.calls:
                temp = text
                text = text.replace(self.calls[c].get_code(), "")
                if(temp==text):
                    raise Exception("This souldn't happen")
            for match in re.finditer(pattern_call, text):
                if(match.group(1) in to_call):
                    start, end = match.span(0)
                    #We do this cause the first caracter is a " "
                    start+=1
                    searching=True
                    call_code = get_end_call(text, start, end)
                    try:
                        OG_code=self.dico_OG_call_2_new_call[call_code]
                        call = Call(code =call_code, origin =self, OG_code=OG_code)
                    except:
                        call = Call(code =call_code, origin =self)
                    call.initialise()
                    self.calls[str(call)] = call
                    break

        #pattern_call_pipe = r"\|\s*(\w+)"
        #searching = True
        #while(searching):
        #    searching= False
        #    text = self.get_code(clean_pipe = clean_pipe)
        #    
        #    for c in self.calls:
        #        text = text.replace(self.calls[c].get_code(), "")
        #    for match in re.finditer(pattern_call_pipe, text):
        #        if(match.group(1) in to_call):
        #            start, end = match.span(0)
        #            from .outils import checks_in_condition_if, checks_in_string, extract_inside_parentheses
        #            if(not checks_in_condition_if(text, match.group(1)) and not checks_in_string(text, match.group(1))):
        #                searching=True
        #                call = Call(code =extract_inside_parentheses(text, match.group(1)), origin =self)
        #                call.initialise()
        #                self.calls[str(call)] = call
        #                break
  
    #Returns if the code if a double dot pattern or not
    def check_if_double_dot(self):
        pattern = constant.DOUBLE_DOT
        is_a_match = bool(re.fullmatch(pattern, self.get_code(clean_pipe = False)))
        if(is_a_match):
            is_good = True
            for match in re.finditer(pattern, self.get_code(clean_pipe = False)):
                if(get_curly_count(match.group(2))!=0 or get_curly_count(match.group(3))!=0):
                    is_good= False
            return is_good

        else:
            return False

    #This method is to flag cases of ch = call(ch) or call(ch)\n ch = emit.call.out
    def check_that_operation_does_not_create_loop_with_call(self):
        for o in self.origins:
            if(o.get_type()=='Call' or o.get_type()=='Emitted'):
                if(o.get_type()=='Emitted'):
                    call = o.emitted_by
                else:
                    call = o
                for param in call.get_parameters():
                    for g in self.gives:
                        if(g.get_code(get_OG = True)==param.get_code(get_OG = True)):
                            self.create_loop_with_call = True
                


    def initialise(self):
        #If the operation is a double dot consition thing
        if(self.check_if_double_dot()):
            self.initialise_double_dot()
        elif(bool(re.fullmatch(constant.DOUBLE_DOT_TUPLE, self.get_code(clean_pipe = False)))):
            raise BioFlowInsightError("tco", self, self.get_string_line(self.get_code(clean_pipe = False)))
        else:
            self.extract_calls()
            self.initialise_origins()
            self.initialise_gives()
            self.check_that_operation_does_not_create_loop_with_call()

        self.write_summary(self.get_output_dir() / "debug/operations.nf")
        
    def check_if_empty_call(self):
        return self.get_code()==""
    
    #This method returns the element which is defined after the call
    def get_element_after_call(self, call):
        for match in re.finditer(str(call)+r"\s*\.\s*(\w+)\s*\.", self.get_code()):
            return match.group(1)


    


    def initialise_from_call(self):
        if(self.get_code()!="" and self.get_code()[0]=="[" and self.get_code()[-1]=="]"):
            None
            #TODO
            #basically in this code -> i want to do the same thing for analye_parameters for a call
            #But instead of adding them to the params, adding them to the gives..
            #Cause in the list you can put anything really
            
        #Working here
        if(self.get_code()!=""):
            self.extract_calls()
            self.initialise_gives()
            self.initialise_origins()
            self.gives+=self.origins
            self.gives = list(set(self.gives))
            #TODO -> this was originally uncommented, check it doesn't add any other bugs
            #self.origins = []
            #warnings.warn(f"TO CHECK !! From this : '{self.get_code()}'. I extracted to give (for a call) '{self.gives}' (in file '{self.get_file_address()}')\n")
            #TODO
            #We check that the operation is an actuel operation and not just a string for example
            #if(len(self.get_origins())==0 and len(self.get_gives())==0):
            #    self.show_in_structure = False
        self.write_summary(self.get_output_dir() / "debug/operations_in_call.nf")

    def get_structure(self, dico, to_remove = False):
        code = self.get_code(replace_calls=False)
        #Need to replace /* and */ by /\* and *\/ so graphivz doesn't think it's a comment
        #Same for // -> replace it by /\/\
        code = code.replace("/*", "/\*").replace("*/", "*\/").replace("//", "/\/\\")
        code = code.replace('"', "'")
        if(self.get_operation_type()=="Branch"):
            fillcolor = "white"
        else:
            fillcolor = ""


        dico['nodes'].append({'id':str(self), 'name':"", "shape":"point", 'xlabel': code, 'fillcolor':fillcolor, "artificial": self.get_artificial_status()})

        for o in self.origins:
            #Case origins is a channel
            if(o.get_type()=="Channel"):
                channel = o
                channel.get_structure(dico, B=self)

            #Case origins is a call
            elif(o.get_type()=="Call"):
                call = o
                call.get_structure(dico)
                #Case the first call is a process
                if(call.get_first_element_called().get_type()=="Process"):
                    dico["edges"].append({'A':str(call.get_first_element_called()), 'B':str(self), "label":""})#TODO check name of channel
                #Case the first call is a subworkflow
                elif(call.get_first_element_called().get_type()=="Subworkflow"):
                    sub = call.get_first_element_called()
                    if(sub.get_nb_emit()==0):
                        raise BioFlowInsightError("sen", self, sub.get_name(), self.get_string_line(call.get_code(get_OG = True)))
                    elif(sub.get_nb_emit()>1):
                        #In the case test().a.view() and test is a subworkflow
                        added = False
                        element_after_call = self.get_element_after_call(o)
                        emits = sub.get_emit()
                        for e in emits:
                            if(e.get_gives()==[]):
                                for o in e.get_origins():
                                    if(o.get_code()==element_after_call):
                                        dico["edges"].append({'A':str(e), 'B':str(self), "label":e.get_code()})
                                        added =True
                            else:
                                for g in e.get_gives():
                                    if(g.get_code()==element_after_call):
                                        dico["edges"].append({'A':str(e), 'B':str(self), "label":e.get_code()})
                                        added =True
                        
                        if(not added):
                            raise BioFlowInsightError("tmctu", self, sub.get_name(), self.get_string_line(call.get_code()))
                        
                    else:
                        emit = sub.get_emit()[0]
                        dico["edges"].append({'A':str(emit), 'B':str(self), "label":emit.get_code()})
                    #for out in sub.get_emit():
                    #    #These are channels
                    #    #TODO check this -> it was the one line 644 before
                    #    #out.get_structure(dico, B=self)
                    #    out.get_structure(dico)
                elif(call.get_first_element_called().get_type()=="Function"):
                    #TODO check if this is actually the cas
                    None
                else:
                    raise Exception("This souldn't happen!")
                
            
            #Case origins is a Emmited
            elif(o.get_type()=="Emitted"):
                emitted = o
                emitted.get_structure(dico, B=self)
            else:
                raise Exception(f"This souldn't happen! The origin of an operation is of type '{o.get_type()}'. It's code is '{o.get_code()}'")
                
    def convert_to_DSL2(self):
        code = self.get_code(get_OG=True)
        return operation_2_DSL2(code, self)
    
    #Method that rewrites operations to simplify it -> decompose it into multiple line -> to be able to manipulate the calls in a easier way
    def simplify_code(self, return_tab):
        code = self.get_code(replace_calls =False, clean_pipe=True, remove_emit_and_take=True)
        #code = self.get_code(get_OG=True)
        index = 1
        operation_id = str(self)[-7:-2]

        def add_origin_equals(call, index):
            simplified_code = call.simplify_code(return_tab = False)
            lines = simplified_code.split('\n')
            return f"{simplified_code}\noperation_{operation_id}_{index} = {call.get_first_element_called().get_alias_and_id()}.out[0]"
            #if(len(lines)==1):
            #    return f"operation_{operation_id}_{index} = {simplified_code}"
            #else:
            #    head = '\n'.join(lines[:-1])
            #    return f"{head}\noperation_{operation_id}_{index} = {lines[-1]}"

        to_add = []
        dico_origin_2_replace = {}
        for o in self.origins:
            #OG_code = o.get_code(get_OG=True)
            OG_code = o.get_code(replace_calls =False, clean_pipe=True, remove_emit_and_take=True)
            try:
                tmp = dico_origin_2_replace[OG_code]
            except:
                dico_origin_2_replace[OG_code] = []
            if(o.get_type()=="Call"):
                #If it's not a function -> then we rewrite it
                if(o.get_first_element_called().get_type()!="Function"):
                    to_add.append(add_origin_equals(o, index))
                    dico_origin_2_replace[OG_code].append(f"operation_{operation_id}_{index}")
            elif(o.get_type()=="Emitted"):
                dico_origin_2_replace[OG_code].append(o)
            elif(o.get_type()=="Channel"):
                #dico_origin_2_replace[OG_code].append(o)
                None
            else:
                raise Exception("This shoudn't happen")
            index += 1
        
        temporary_index = 1
        new_body = ""
        for origin in dico_origin_2_replace:
            if(len(dico_origin_2_replace[origin])<=1):
                for val in dico_origin_2_replace[origin]:
                    temp = code
                    if(type(val)==str):
                        code = code.replace(origin, val)
                    else:
                        code = code.replace(origin, val.simplify_code(return_tab = False))
                    if(temp==code):
                        raise Exception("This souldn't happen")
            #Case there are mutiple origins then:
            else:
                
                
                temporary_channel = f"temporary_val_{id(self)}_{temporary_index}"
                types = []
                for e in dico_origin_2_replace[origin]:
                    types.append(e.get_type())
                

                if(set(types)=={"Emitted"}):
                    #Case the multiple origins are emits
                    #For example 
                    #if(){
                    #   p1(ch1)
                    #} else {
                    #   p1(ch2)
                    #}
                    #val = p1.out -> when wanting to rewrite this operation
                    calls = {}
                    for e in dico_origin_2_replace[origin]:
                        try:
                            temp = calls[e.emitted_by]
                        except:
                            calls[e.emitted_by] = []
                        calls[e.emitted_by].append(e.simplify_code(return_tab = False))
                    for c in calls:
                        #This is just one value
                        if(len(c.get_all_conditions())>1):
                            raise Exception("This shoudn't happen")
                        conditions = c.get_all_conditions()
                        if(conditions!=[]):
                            for condition in conditions:
                                new_body+=f"if({condition.get_value().strip()}) {{\n{temporary_channel} = {calls[c][0]}\n}}\n"
                        else:
                            values = set(calls[c])
                            if(len(values)>1):
                                raise Exception("This souldn't happen")
                            for val in values:
                                new_body+=f"\n{temporary_channel} = {val}"
                
                #Case the multiple origins are channels
                #For example 
                #if(){
                #   a = ...
                #} else {
                #   a = ...
                #}
                #b = a -> when wanting to rewrite this operation
                elif(set(types)=={"Channel"}):
                    None
                    #operations = {}
                    #for c in dico_origin_2_replace[origin]:
                    #    for source in c.get_source():
                    #        try:
                    #            temp = operations[source]
                    #        except:
                    #            operations[source] = []
                    #        operations[source].append(c.simplify_code(return_tab = False))
                    #for o in operations:
                    #    #Turning into one condition
                    #    conditions = []
                    #    for condition in o.get_all_conditions():
                    #        conditions.append(condition.get_value().strip())
                    #    if(conditions!=[]):
                    #        new_body+=f"if({' && '.join(conditions)}) {{\n{temporary_channel} = {operations[o][0]}\n}}\n"
                    #    else:
                    #        values = set(operations[o])
                    #        if(len(values)>1):
                    #            raise Exception("This souldn't happen")
                    #        for val in values:
                    #            new_body+=f"\n{temporary_channel} = {val}"
                else:
                    raise Exception("This shoudn't happen")
                
                
                #new_body+=temporary_channel
                temp = code
                code = code.replace(origin, temporary_channel)
                if(temp==code):
                    raise Exception("This souldn't happen")
                temporary_index+=1
                to_add.append(new_body)
        to_add.reverse()
        if(return_tab):
            last_operation = code
            return to_add, last_operation
        else:
            for c in to_add:
                code = f"{c}\n{code}"
            return code
            
        
                

