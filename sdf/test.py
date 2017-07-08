# Copyright (c) 2017 Dassault Systemes. All rights reserved.
import runpy
import unittest
import numpy as np
import math
import sdf
import os


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import matplotlib.pyplot as plt

        def no_show():
            pass

        # suppress matplotlib.pyplot.show()
        plt.show = no_show

    def assertDatasetsEqual(self, ds1, ds2):

        # compare string attributes
        for attr in ['name', 'comment', 'display_name', 'relative_quantity', 'unit', 'display_unit']:
            a = getattr(ds1, attr)
            b = getattr(ds2, attr)
            self.assertEqual(a, b)

        # compare data
        self.assertTrue(np.all(ds1.data == ds2.data))

    def test_data_types(self):

        ds_f = sdf.Dataset(name='f', data=np.asarray([1, 2, 3], dtype=np.float32))
        ds_d = sdf.Dataset(name='d', data=np.asarray([1, 2, 3], dtype=np.float64))
        ds_i = sdf.Dataset(name='i', data=np.asarray([1, 2, 3], dtype=np.int32))

        g = sdf.Group(name='/', datasets=[ds_f, ds_d, ds_i])

        sdf.save('data_types.sdf', g)

        g = sdf.load('data_types.sdf')

        self.assertEqual(g['f'].data.dtype, np.float32)
        self.assertEqual(g['d'].data.dtype, np.float64)
        self.assertEqual(g['i'].data.dtype, np.int32)

    def test_roundtrip(self):
        
        # create a scale
        ds1 = sdf.Dataset('DS1',
                          comment="dataset 1",
                          data=np.array([0.1, 0.2, 0.3]),
                          display_name='Scale 1',
                          unit='U1',
                          display_unit='DU1',
                          is_scale=True)
        
        # create a 1D dataset
        ds2 = sdf.Dataset('DS2',
                          comment="dataset 2",
                          data=np.array([1, 2, 3]),
                          display_name='Dataset 2',
                          relative_quantity=True,
                          unit='U2',
                          display_unit='DU2',
                          scales=[ds1])
        
        # create a group
        g = sdf.Group(name='/',
                      comment="my comment",
                      attributes={'A1': 'my string'},
                      datasets=[ds1, ds2])
        
        g2 = sdf.Group(name='G2')
        g.groups.append(g2)
        
        # save the group
        sdf.save('test.sdf', g)

        # load DS2 from the file        
        ds2r = sdf.load('test.sdf', '/DS2')

        # make sure the content is still the same
        self.assertDatasetsEqual(ds2, ds2r)
        self.assertDatasetsEqual(ds2.scales[0], ds2r.scales[0])

    def test_hierarchy(self):
        
        # create a scale
        ds_time = sdf.Dataset('Time',
                          comment="A scale",
                          data=np.linspace(0, 10, 101),
                          unit='s',
                          is_scale=True)
        
        ds_sine = sdf.Dataset('sine',
                          comment="A 1-d dataset /w attached scale",
                          data=np.sin(ds_time.data),
                          scales=[ds_time])
        
        # create the root group
        g = sdf.Group(name='/',
                      comment="A test file",
                      attributes={'A1': "my string"},
                      datasets=[ds_time, ds_sine])

        # create a scalar dataset
        ds_alpha = sdf.Dataset('alpha',
                          comment="A scalar /w unit, display unit and display name",
                          data=np.pi,
                          display_name='Angle',
                          unit='rad',
                          display_unit='deg')

        # create a sub group
        g1 = sdf.Group(name='g1',
                      comment="A sub-group",
                      attributes={'A2': "Attribute in sub group"},
                      datasets=[ds_alpha])

        g.groups.append(g1)

        # save the group
        sdf.save('roundtrip.sdf', g)
        
        # load the group from the file        
        g2 = sdf.load('roundtrip.sdf', '/')
         
        # TODO: compare the objects
        #self.assertEqual(pickle.dumps(g), pickle.dumps(g2))
        
    def test_3D_example(self):
        
        RPM2RADS = 2 * math.pi / 60
        
        kfric  = 1       # [Ws/rad] angular damping coefficient [0;100]
        kfric3 = 1.5e-6  # [Ws3/rad3] angular damping coefficient (3rd order) [0;10-3]
        psi    = 0.2     # [Vs] flux linkage [0.001;10]
        res    = 5e-3    # [Ohm] resistance [0;100]
        v_ref  = 200     # [V] reference DC voltage [0;1000]
        k_u    = 5       # linear voltage coefficient [-100;100]
    
        tau = np.arange(0.0, 230.0 + 10.0, 10)
        w = np.concatenate((np.arange(0.0, 500.0, 100), np.arange(500.0, 12e3+500, 500))) * RPM2RADS
        u = np.asarray([200.0, 300.0, 400.0])
    
        # calculate the power losses
        TAU, W, U = np.meshgrid(tau, w, u, indexing='ij')
    
        P_loss = kfric * W + kfric3 * W ** 3 + (res * (TAU / psi) ** 2) + k_u * (U - v_ref)
    
        # create the scales
        ds_tau = sdf.Dataset('tau',
                          comment='Torque',
                          data=tau,
                          display_name='Torque',
                          unit='N.m',
                          is_scale=True)
        
        ds_w = sdf.Dataset('w',
                          comment='Speed',
                          data=w,
                          display_name='Speed',
                          unit='rad/s',
                          display_unit='rpm',
                          is_scale=True)
        
        ds_v = sdf.Dataset('v',
                          comment='DC voltage',
                          data=u,
                          display_name='DC voltage',
                          unit='V',
                          is_scale=True)
        
        # create the dataset
        ds_P_loss = sdf.Dataset('P_loss',
                          comment='Power losses',
                          display_name='Power Losses',
                          data=P_loss,
                          unit='W',
                          scales=[ds_tau, ds_w, ds_v])
        
        # create a group
        g = sdf.Group(name='/',
                      comment="Example loss characteristics of an e-machine w.r.t. torque, speed and DC voltage",
                      datasets=[ds_tau, ds_w, ds_v, ds_P_loss])

        errors = sdf.validate(g)
        self.assertEqual([], errors)
        
        sdf.save('emachine.sdf', g)
        
    def test_validate_group(self):
        g = sdf.Group('8')    
        errors = sdf._validate_group(g, is_root=False)
        self.assertEqual(["Object names must only contain letters, digits and underscores (\"_\") and must start with a letter"], errors)
        
        g.name = 'G1'
        errors = sdf._validate_group(g, is_root=False)
        self.assertEqual([], errors)

    def test_validate_dataset(self):
        ds1 = sdf.Dataset('DS1')
             
        ds1.data = 1
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(["Dataset.data must be a numpy.ndarray"], errors)
        
        ds1.data = np.array([])
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(["Dataset.data must not be empty"], errors)

        ds1.data = np.array(1).astype(np.float32)
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(["Dataset.data.dtype must be numpy.float64"], errors)
        
        ds1.data = np.array([1.0, 2.0])
        errors = sdf._validate_dataset(ds1)
        self.assertEqual(["The number of scales does not match the number of dimensions"], errors)

        ds2 = sdf.Dataset('DS2', data=np.array([0.0, 1.0, 2.0]), is_scale=True)
        ds1.scales = [ds2]
        errors = sdf._validate_dataset(ds1)
        self.assertEqual([], errors)
        
        ds2.data = np.array([[1.0, 2.0], [3.0, 4.0]])
        errors = sdf._validate_dataset(ds2)
        self.assertEqual(["Scales must be one-dimensional"], errors)
        
        ds2.data = np.array([0, 1.0, 1.0])
        errors = sdf._validate_dataset(ds2)
        self.assertEqual(["Scales must be strictly monotonic increasing"], errors)

    def test_dsres_load_all(self):
        path, _ = os.path.split(__file__)
        filename = os.path.join(path, 'examples', 'IntegerNetwork1.mat')

        g = sdf.load(filename)

        s = g['Time']
        self.assertEqual(s.data.size, 552)
        self.assertEqual(s.data.dtype, np.float32)
        self.assertEqual(s.unit, 's')
        self.assertEqual(s.comment, 'Simulation time')

        ds = g['booleanPulse2']['period']
        self.assertEqual(ds.data, 2.0)
        self.assertEqual(ds.data.dtype, np.float32)
        self.assertEqual(ds.unit, 's')
        self.assertEqual(ds.comment, 'Time for one period')

        ds = g['booleanPulse2']['y']
        self.assertEqual(ds.data.dtype, np.int32)
        self.assertEqual(ds.data.size, 552)
        self.assertEqual(ds.data[0], True)
        self.assertEqual(ds.data[93], False)
        self.assertEqual(ds.scales[0], s)

        ds = g['integerConstant']['k']
        self.assertEqual(ds.data.dtype, np.int32)
        self.assertEqual(ds.data, 1)

        # sdf.save(filename=os.path.join(path, 'examples', 'IntegerNetwork1.sdf'), group=g)

    def test_dsres_load_dataset(self):

        path, _ = os.path.split(__file__)
        filename = os.path.join(path, 'examples', 'IntegerNetwork1.mat')

        ds = sdf.load(filename, objectname='/booleanPulse2/period')

        self.assertEqual(ds.data, 2.0)
        self.assertEqual(ds.data.dtype, np.float32)
        self.assertEqual(ds.unit, 's')
        self.assertEqual(ds.comment, 'Time for one period')

        ds = sdf.load(filename, objectname='/booleanPulse2/y')
        self.assertEqual(ds.data.dtype, np.int32)
        self.assertEqual(ds.data.size, 552)
        self.assertEqual(ds.data[0], True)
        self.assertEqual(ds.data[93], False)

        s = ds.scales[0]
        self.assertEqual(s.data.size, 552)
        self.assertEqual(s.data.dtype, np.float32)
        self.assertEqual(s.unit, 's')
        self.assertEqual(s.comment, 'Simulation time')

        ds = sdf.load(filename, objectname='/integerConstant/k')
        self.assertEqual(ds.data.dtype, np.int32)
        self.assertEqual(ds.data, 1)

    # def test_excel2sdf_example(self):
    #     path, _ = os.path.split(__file__)
    #     filename = os.path.join(path, 'examples', 'excel2sdf.py')
    #     runpy.run_path(filename)

    def test_interp_1d_example(self):
        path, _ = os.path.split(__file__)
        filename = os.path.join(path, 'examples', 'interp_1d.py')
        runpy.run_path(filename)

    def test_interp_2d_example(self):
        path, _ = os.path.split(__file__)
        filename = os.path.join(path, 'examples', 'interp_2d.py')
        runpy.run_path(filename)

    def test_sine_example(self):
        path, _ = os.path.split(__file__)
        filename = os.path.join(path, 'examples', 'sine.py')
        runpy.run_path(filename)

    def test_spline_1d_example(self):
        path, _ = os.path.split(__file__)
        filename = os.path.join(path, 'examples', 'spline_1d.py')
        runpy.run_path(filename)

if __name__ == "__main__":
    unittest.main()
