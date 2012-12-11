import os
import sys;sys.path.append(os.path.join("..",".."))
import unittest
from operator import itemgetter
from netpython import eden


class TestEden(unittest.TestCase):
    
	def setUp(self):
		self.folder=os.path.dirname(eden.__file__)+os.path.join("a","tests","")[1:]
		self.data1=["100 101 200 220 330 300",
			    "101 102 201 221 301 331"]
		self.data2=["100 101 200 220 330 999",
			    "101 999 201 221 301 331"]
		self.data3=["123 999 999",
			    "123 123 999",
			    "999 123 123"]

		self.data_nonnumeric1=["A A B A B C",
				       "A A 999 B A C"]

		self.data_nonnumeric2=["A A B A B C",
				       "A A B A B C",
				       "A A 999 B A C",
				       "A A 999 B A C"]

		self.binary_data1=["1 1 1 1",
				  "1 0 0 0",
				  "0 1 1 1"]
		self.binary_data_broken1=["1 999",
					 "1 1"]
		self.binary_data_broken2=["1 1 1",
					 "1 1"]

		self.abundance_data1=["0 0 1",
				     "0 0 2",
				     "1 1 1"]
		self.msat_data_filename=os.path.join("testData","msat_testdata.txt")

	def test_distances_abundances(self):
		data1=eden.MicrosatelliteDataHaploid(self.abundance_data1)
		dm1=data1.getDistanceMatrix(distance="czekanowski")
		assert dm1[0,1]==1-2/3.0 and dm1[0,2]==1-0.5 and dm1[1,2]==1-0.4

	def test_distances_allele_freqs(self):
		ms1=eden.MicrosatelliteDataHaploid(self.data_nonnumeric2)
		af1=eden.AlleleFrequencyTable()
		try:
			af1.init_msData(ms1,[[0,1],[2,3]])
		except eden.EDENException,e:
			assert "input data has" in str(e)

		af2=eden.AlleleFrequencyTable()
		af2.init_msData(ms1,[[0,2],[1,3]])
		assert af2.freqsTable[0]==[{'A':2},{'A':2},{'B':1},{'A':1,'B':1},{'B':1,'A':1},{'C':2}]
		assert af2.freqsTable[1]==[{'A':2},{'A':2},{'B':1},{'A':1,'B':1},{'B':1,'A':1},{'C':2}]

		ms1=eden.MicrosatelliteData(self.data_nonnumeric2)
		af3=eden.AlleleFrequencyTable()
		af3.init_msData(ms1,[[0,2],[1,3]])
		self.assertEqual(af3.freqsTable[0],[{'A':4},{'A':1,'B':2},{'B':1,'A':1,'C':2}])

	def test_distances_allele_freqs_msat(self):
		af=eden.AlleleFrequencyTable()
		af.init_freqFile(self.msat_data_filename)
		d=af.getFST()
		self.assertEqual(round(d["CAR","CIN"],3),0.075)
		self.assertEqual(round(d["CAM","CIN"],3),0.025)
		self.assertEqual(round(d["CAR","CAM"],3),0.088)


	def test_distances_binary_data(self):
		bd1=eden.BinaryData()
		bd1.read_file(self.binary_data1)
		dm1=bd1.get_distance_matrix("jaccard_distance",["a","b","c"])
		assert dm1["a","b"]==1-1./4. and dm1["a","c"]==1-3./4. and dm1["b","c"]==1.0

		bd2=eden.BinaryData()
		exception_ok=False
		try:
			bd2.read_file(self.binary_data_broken1)
		except eden.ParsingError,e:
			if "Invalid element" in str(e):
				exception_ok=True
		assert exception_ok, "No/invalid exception on invalid data!"

		bd3=eden.BinaryData()
		exception_ok2=False
		try:
			bd3.read_file(self.binary_data_broken2)
		except eden.ParsingError,e:
			if "features" in str(e):
				exception_ok2=True
		assert exception_ok2, "No/invalid exception on invalid data."


	def test_distances_individuals(self):
		#Diploid
		ms1=eden.MicrosatelliteData(self.data1)
		dm1=ms1.getDistanceMatrix(distance="lm")
		assert dm1[0,1]==2.0,"Diploid data: Error calculating the linear manhattan distance."
		dm2=ms1.getDistanceMatrix(distance="ap")
		assert dm2[0,1]==(1.0+2.0+2.0)/3.0,"Diploid data: Error calculating the allele parsimony distance."

		#Haploid
		ms2=eden.MicrosatelliteDataHaploid(self.data1)
		dm3=ms2.getDistanceMatrix(distance="lm")
		assert dm3[0,1]==(4*1.0+29.0+31.0)/6.0,"Haploid data: Error calculating the linear manhattan distance."
		dm4=ms2.getDistanceMatrix(distance="ap")
		assert dm4[0,1]==1.0,"Haploid data: Error calculating the allele parsimony distance."		

	def test_distances_populations(self):
		#Diploid
		ms1=eden.MicrosatelliteData(self.data1)
		dm1=ms1.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein_d1")
		assert dm1[0,1]==0.25*((1+4+1)+(1+21*21+19*19+1)+(29*29+1+1+31*31))/3.0,"Diploid data: Error calculating the goldstein D1 distance."

		dm3=ms1.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein")
		assert dm3[0,1]==(((100+101)/2.-(101+102)/2.)**2+((200+220)/2.-(201+221)/2.)**2+((330+300)/2.-(301+331)/2.)**2)/3.,"Diploid data: Error calculating the goldstein distance."

		#Haploid
		ms2=eden.MicrosatelliteDataHaploid(self.data1)
		dm2=ms2.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein_d1")
		assert dm2[0,1]==(1+1+1+1+29*29+31*31)/6.0,"Haploid data: Error calculating the goldstein D1 distance."

		dm4=ms2.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein")
		assert dm4[0,1]==(1+1+1+1+29*29+31*31)/6.0,"Haploid data: Error calculating the goldstein distance."


	def test_distances_individuals_nonnumeric(self):
		ms1=eden.MicrosatelliteDataHaploid(self.data_nonnumeric1)
		dm1=ms1.getDistanceMatrix(distance="ap")
		assert dm1[0,1]==1.-3./5., "Error calculating the allele parsimony distance for non-numeric data."

	def test_distances_individuals_missing_data(self):		
		#Diploid
		ms1=eden.MicrosatelliteData(self.data2)
		dm1=ms1.getDistanceMatrix(distance="lm")
		assert dm1[0,1]==2.0,"Diploid data: Error calculating the linear manhattan distance."
		dm2=ms1.getDistanceMatrix(distance="ap")
		assert dm2[0,1]==2.0,"Diploid data: Error calculating the allele parsimony distance."

		#Haploid
		ms2=eden.MicrosatelliteDataHaploid(self.data2)
		dm3=ms2.getDistanceMatrix(distance="lm")
		assert dm3[0,1]==(3*1.0+29.0)/4.0,"Haploid data: Error calculating the linear manhattan distance."
		dm4=ms2.getDistanceMatrix(distance="ap")
		assert dm4[0,1]==1.0,"Haploid data: Error calculating the allele parsimony distance."	

		#Haploid, large amounts of missing data
		ms3=eden.MicrosatelliteDataHaploid(self.data3)
		dm5=ms3.getDistanceMatrix(distance="lm")
		assert dm5[0,1]==0.0,"Missing data: Error."
		assert dm5[0,2]==-1, "Missing data: No matchind data fields should lead to -1 distance."
		#print list(dm5.edges)


	def test_distances_populations_missing_data(self):
		#Diploid
		ms1=eden.MicrosatelliteData(self.data2)
		dm1=ms1.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein_d1")
		assert dm1[0,1]==(0.5*1+0.25*(1+21*21+19*19+1)+0.5*(29*29+1))/3.0,"Diploid data: Error calculating the goldstein D1 distance."

		dm3=ms1.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein")
		assert dm3[0,1]==(((100+101)/2.-(101)/1.)**2+((200+220)/2.-(201+221)/2.)**2+((330)/1.-(301+331)/2.)**2)/3.,"Diploid data: Error calculating the goldstein distance."

		#Haploid
		ms2=eden.MicrosatelliteDataHaploid(self.data2)
		dm2=ms2.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein_d1")
		assert dm2[0,1]==(1+1+1+29*29)/4.0,"Haploid data: Error calculating the goldstein D1 distance."

		dm4=ms2.getGroupwiseDistanceMatrix(groups=[[0],[1]],distance="goldstein")
		assert dm4[0,1]==(1+1+1+29*29)/4.0,"Haploid data: Error calculating the goldstein distance."




			
if __name__ == '__main__':
	if True:
		# If true, run only the tests listed below, otherwise run all tests
		# (this option is for testing the tests :-) )
		suite = unittest.TestSuite()
		suite.addTest(TestEden("test_distances_abundances"))
		suite.addTest(TestEden("test_distances_allele_freqs"))
		suite.addTest(TestEden("test_distances_allele_freqs_msat"))
		suite.addTest(TestEden("test_distances_binary_data"))
		suite.addTest(TestEden("test_distances_individuals"))
		suite.addTest(TestEden("test_distances_populations"))
		suite.addTest(TestEden("test_distances_individuals_nonnumeric"))
		suite.addTest(TestEden("test_distances_individuals_missing_data"))
		suite.addTest(TestEden("test_distances_populations_missing_data"))
		unittest.TextTestRunner().run(suite)
	else:
		# Run all tests.
		unittest.main()
