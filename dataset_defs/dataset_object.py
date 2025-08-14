import math
import re
from .DatasetDictionaryDef import DatasetDict

GENERATORS = {
        'Agrawal': {
                'fullName':'AgrawalGenerator',
                'functions': list(range(1,12))
        },
        'STAGGER': {
                'fullName':'STAGGERGenerator',
                'functions':list(range(1,4))
        },
        'SEA': {
                'fullName':'SEAGenerator',
                'functions': list(range(1,5))
        }
}

class DatasetObject:
        generator: str
        classification_functions: list[int]
        drift_points: list[int]
        drift_widths: list[int]
        num_of_samples: int

        def __init__(self):
                self.generator = ''
                self.classification_functions = []
                self.drift_points = []
                self.drift_widths = []
                self.num_of_samples = 0    


        def from_base_values(self,generator:str,classification_functions:list[int],drits_points:list[int], drift_widths:list[int],number_of_samples:int):
                self.generator = generator
                self.classification_functions = classification_functions
                self.drift_points = drits_points
                self.drift_widths = drift_widths
                self.num_of_samples = number_of_samples
                self._validate()
        
        def from_string(self, generator_string: str):
                pattern = re.compile(
                r'^(?P<name>[^_]+)'            # generator name (no underscores)
                r'_f_(?P<f_vals>\d+(?:_\d+)*)' # f values (one or more ints separated by _)
                r'(?:_p_(?P<p_vals>\d+(?:_\d+)*)_w_(?P<w_vals>\d+(?:_\d+)*))?'  # optional p and w blocks
                r'_s_(?P<s>\d+)$'              # final s integer
                )

                m = pattern.fullmatch(generator_string)
                if(not m):
                        raise Exception(f'INVALID STRING PASSED FOR PARSING: {generator_string}')
                
                self.generator = m.group('name')
                self.classification_functions = [int(x) for x in m.group('f_vals').split('_')]
                if(m.group('p_vals')):
                        self.drift_points = [int(x) for x in m.group('p_vals').split('_')]
                        self.drift_widths = [int(x) for x in m.group('w_vals').split('_')]
                else:
                        self.drift_points = []
                        self.drift_widths = []
                self.num_of_samples = int(m.group('s'))
                
                self._validate()
        
        def from_dict(self, generation_dict: DatasetDict):
                if(not isinstance(generation_dict, dict)):
                        raise Exception('VALUE PASSED TO GENERATION OBJECT IS NOT A PROPER DICTIONARY')
                all_keys = {'generator','classification_functions','drift_points','drift_widths','num_of_samples'}
                shorthand_keys = {'generator','classification_functions','num_of_samples'}
                if(generation_dict.keys() != all_keys and generation_dict.keys() != shorthand_keys):
                        raise Exception(f'DICTIONARY PASSED TO GENERATION OBJECT DOES NOT COMPLY TO THE NECESSARY STRUCTURE. ACCEPTED STRUCTURES: \n {all_keys} \n {shorthand_keys}')
                
                if(not isinstance(generation_dict['classification_functions'], list)):
                        raise Exception('classification_functions FIELD MUST BE A LIST') 
                if('drift_points' in generation_dict.keys() and not isinstance(generation_dict['drift_points'], list)):
                        raise Exception('drift_points FIELD MUST BE A LIST') 
                if('drift_widths' in generation_dict.keys() and not isinstance(generation_dict['drift_widths'], list)):
                        raise Exception('drift_widths FIELD MUST BE A LIST') 

                self.generator = generation_dict['generator']
                self.classification_functions = generation_dict['classification_functions']
                if('drift_points' in generation_dict.keys()):
                        self.drift_points = generation_dict['drift_points']
                        self.drift_widths = generation_dict['drift_widths']
                self.num_of_samples = int(generation_dict['num_of_samples'])
                self._validate()
        
        
        def to_string(self) -> str:
                self._validate()
                res = self.generator + '_'
                
                res+= 'f_'
                for function in self.classification_functions:
                        res+=str(function)+'_'
                
                if(len(self.drift_points)):
                        res+='p_'
                        for point in self.drift_points:
                                res+=str(point)+'_'
                
                if(len(self.drift_widths)):
                        res+='w_'
                        for width in self.drift_widths:
                                res+=str(width)+'_'
                
                res+='s_'+str(self.num_of_samples)
                return res    

        def get_generator_name(self) -> str:
                return GENERATORS[self.generator]['fullName'] 


        def _validate(self):
                if(self.generator not in GENERATORS.keys()):
                        raise Exception(f'INVALID GENERATOR TYPE "{self.generator}". SUPPORTED GENERATORS: {GENERATORS.keys()}')
                if(len(self.classification_functions) <=0):
                        raise Exception(f'MUST PROVIDE AT LEAST ONE CLASSIFICATION FUNCTION')
                
                for funct in self.classification_functions:
                        if(not isinstance(funct,int)):
                                raise Exception('ALL CLASSIFICATION FUNCTION VALUES MUST BE AN INTEGER')
                        if(not funct in GENERATORS[self.generator]['functions']):
                                raise Exception(f'PROVIDED CLASSIFICATION FUNCTION IS NOT SUPPORTED BY THIS GENERATOR. AVAILABLE FUNCTIONS: {GENERATORS[self.generator]['functions']}')
                for point in self.drift_points:
                        if(not isinstance(point,int)):
                                raise Exception('ALL DRIFT POINT VALUES MUST BE AN INTEGER')
                for width in self.drift_widths:
                        if(not isinstance(width,int)):
                                raise Exception('ALL DRIFT WIDTH VALUES MUST BE AN INTEGER')

                #Each concept drift requires two classification functions(which can overlap), so the number of functions must be one more than the number of drits
                if((len(self.drift_points) != len(self.drift_widths)) or (len(self.drift_points) != len(self.classification_functions) -1)):
                        raise Exception('THE NUMBER OF CLASSIFICATION FUNCTIONS AND DRIFTS MISMATCH. THERE MUST BE ONE MORE CLASSIFICATION FUNCTION THAN THE NUMBER OF DRIFT POINTS')
                #Make sure the drift points are strictly raising
                for i in range(1,len(self.drift_points)):
                        if(self.drift_points[i-1]>=self.drift_points[i]):
                                raise Exception('DRIFT POINTS VALUES MUST BE STRICTLY RAISING')
                #Make sure there is no overlap in the drift area(and that width is over 0)
                drift_areas = []
                for i in range(len(self.drift_points)):
                        if(self.drift_widths[i] < 1):
                                raise Exception('DRIFT WIDTH VALUES MUST BE ABOVE 0')
                        ofset = math.ceil(self.drift_widths[i]/2)
                        lower = self.drift_points[i]-ofset
                        upper = self.drift_points[i]+ofset
                        if(lower<1):
                                raise Exception('ONE OF THE DRIFT AREAS WOULD BEGIN BEFORE FIRST SAMPLE')
                        if(upper>=self.num_of_samples):
                                raise Exception('ONE OF THE DRIFT AREAS WOULD END AFTER THE LAST SAMPLE')
                        if(i>0):
                                if(max(drift_areas)>= lower):
                                        raise Exception(f'ONE OF THE DRIFT AREAS WOULD LEAD TO AN OVERLAP {drift_areas} {lower} {upper}')

                        drift_areas.append(lower)
                        drift_areas.append(upper)
                
                if(self.num_of_samples<=0):
                        raise Exception('MUST SPECIFY NUMBER OF SAMPLES HIGHER THAN ONE')
