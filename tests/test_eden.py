import unittest
from operator import itemgetter
from netpython import eden
import os

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
		suite.addTest(TestEden("test_distances_individuals"))
		suite.addTest(TestEden("test_distances_populations"))
		suite.addTest(TestEden("test_distances_individuals_missing_data"))
		suite.addTest(TestEden("test_distances_populations_missing_data"))
		unittest.TextTestRunner().run(suite)
	else:
		# Run all tests.
		unittest.main()
