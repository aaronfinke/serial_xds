import subprocess, os, re
from generate_xds import gen_xds_text


class Datawell(object):

	# Generating a constructor for the class:
	def __init__(self, first_frame, last_frame, master_directory, masterpath, args):
		self.ff = first_frame
		self.lf = last_frame
		self.master_dir = master_directory
		self.masterpath = masterpath
		self.args = args


		# Variables defined within class:
		self.framepath = "{d}/{start}_{end}".format(d=self.master_dir, start=self.ff, end=self.lf)
		self.results_dict = {}
		self.final_dict = {}
		
		
		# Functions called within class:
		self.setup_datawell_directory() # generating datawell directory
		self.gen_XDS() # generating XDS.INP in datawell directory		
		self.run()		
		
		
		
		
		
	def setup_datawell_directory(self):
		# Generate datawell directory:
		try:
			os.makedirs(self.framepath)
		except OSError:
			print("Failed to create datawell directory")
	
	
		
	def gen_XDS(self):
		# Generating XDS file in datawell directory:
		try:
			d_b_s_range = "{a} {b}".format(a=self.ff, b=self.lf)
			with open(os.path.join(self.framepath, 'XDS.INP'), 'x') as input:
				input.write(gen_xds_text(self.args.unitcell, self.masterpath.replace("master", "??????"),
				self.args.beamcenter[0], self.args.beamcenter[1], self.args.distance, self.args.oscillations,
				self.args.wavelength, d_b_s_range, d_b_s_range, d_b_s_range))
		except:
			print("IO ERROR")
			
			
			
			
	def run(self):
		# Run XDS in the datawell derectory:
		os.chdir(self.framepath)
		#print('xxx {} xxx {} xxx'.format(os.getcwd(), os.listdir(self.framepath)))
		subprocess.call(r"xds_par")
		os.chdir(self.master_dir)
