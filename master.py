import os, sys, h5py, json
import datawell

class Master(object):

	# Generating a constructor for the class:
	def __init__(self, args, masterpath, num_of_total_frames):
		self.args = args
		self.masterpath = masterpath
		self.frames_per_degree = args.framesperdegree
		self.total_frames = num_of_total_frames
		self.output = args.output


		# Variables defined within class:
		self.master_dictionary = {}
		
		# Functions called within class:
		self.create_master_directory() # creating masterfile directories
		self.create_and_run_data_wells() # creating datawell dictionary and run XDS in it
		self.generate_master_dictionary() # creating a master dictionary
		self.write_master_dictionary() # writing a master dictionary as a json file
		
		


	def create_master_directory(self):
		# Generate a name for masterfile directory:
		try:
			end_index = self.masterpath.find('_master.h5')
			start_index = self.masterpath.rfind('/')
			dir_name= self.masterpath[start_index+1:end_index]
			new_dir_path = '{new_dir}/{name}'.format(new_dir = self.output, name = dir_name)
			
			# Create a mesterfile directory:
			try:
				os.makedirs(new_dir_path)
			except OSError:
				print("Creation of the directory {} failed. Such file may already exist.".format(dir_name))
			else:
				print("Successfully created the directory {}".format(dir_name))
		except:
			print("Something is not working. Check the code in 'master.py'")
		
		



	def create_and_run_data_wells(self):
		# Generate datawell directories by creating instances of class called 'Datawell' (from datawell.py):
		for framenum in range(1,self.total_frames,self.frames_per_degree):
			data_well = datawell.Datawell(framenum, framenum+self.frames_per_degree-1, self.get_master_directory_path(), self.masterpath, self.args)
			
	def get_master_directory_path(self):
	 	# Return master directory path. Used in the above function.
			end_index = self.masterpath.find('_master.h5')
			start_index = self.masterpath.rfind('/')
			dir_name= self.masterpath[start_index+1:end_index]
			return '{new_dir}/{name}'.format(new_dir = self.output, name = dir_name)
			
		
		
		
						
	def generate_master_dictionary(self):
		# Generating a master dictionary.
		for datawell in os.listdir(self.get_master_directory_path()):
			frame_dictionary = {}
			full_path = "{}/{}".format(self.get_master_directory_path(), datawell)
			
			# Add 'frame_number' and value to the frame_dictionary:
			name = datawell.replace('_', ' ')
			frame_dictionary['frame_number']=name
			
			# Add 'is_processed' and value to the frame_dictionary:
			processed = os.path.exists('{a}/{b}'.format(a=full_path,b='XDS_ASCII.HKL'))
			frame_dictionary['is_processed']=processed
			
			# Add 'is_indexed' and value to the frame_dictionary:
			frame_dictionary['is_indexed']=processed
			
			# Add 'accepted_reflections' and value to the frame dictionary:
			if processed:
				matching = 'NUMBER OF ACCEPTED OBSERVATIONS (INCLUDING SYSTEMATIC ABSENCES'
				with open('{a}/{b}'.format(a=full_path, b='CORRECT.LP')) as file:
					for line in file:
						if matching in line:
							value = re.search(r'\d+',line)
							frame_dictionary['accepted_reflections']=value.group(0)
							#results_dict['accepted_reflections']= int(value.group(0))
			else:
				frame_dictionary['accepted_reflections']=None

			# Add frame_dictionary to the master_dictionary:
			self.master_dictionary[datawell]=frame_dictionary





	def write_master_dictionary(self):
		# Writing a master dictionary in json file.
		try:
			with open(os.path.join('{}'.format(os.getcwd()), 'DICTIONARY.json'), 'x') as file:
				file.write(json.dumps(self.master_dictionary))
		except FileExistsError:
			print("File 'DICTIONARY.json' already exist")
	
	
	
	
				
# Return number of data files in masterpath by simply finding the length of the H5 group. No checks.
def get_h5_file(path):
	try:
		file = h5py.File(path, 'r')
	except Exception:
		raise IOError("Not a valid h5 file")
	return file
		
def get_number_of_files(path):
	print(path)
	f = get_h5_file(path)
	return len(f['/entry/data'])
    
