"""

Copyright 2019 European Union

Licensed under the EUPL, Version 1.2 or as soon they will be approved by the European Commission  subsequent versions of the EUPL (the "Licence");

You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt

Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and limitations under the Licence.

"""

import os
import numpy as np
from netCDF4 import Dataset
import logging

from lisfloodutilities.cutmaps.main import get_arg_coords

logging.basicConfig(format="%(threadName)s:%(message)s")
from lisfloodutilities import IS_PYTHON2
from lisfloodutilities.cutmaps.cutlib import get_filelist, get_cuts, cutmap, mask_from_ldd
from lisfloodutilities.nc2pcr import convert as nc2pcr_convert
from lisfloodutilities.compare.nc import NetCDFComparator

from . import TestWithCleaner

if IS_PYTHON2:
    from pathlib2 import Path
else:
    from pathlib import Path


class TestCutlib(TestWithCleaner):

    def test_getfiles_to_cut_file(self):
        res = get_filelist(input_file='tests/data/folder_a/ta.nc')
        assert ['tests/data/folder_a/ta.nc'] == res

    def test_getfiles_to_cut_folder(self):
        res = sorted(get_filelist(input_folder='tests/data/folder_a'))
        assert sorted(list(map(Path, ['tests/data/folder_a/ta.nc', 'tests/data/folder_a/tp.nc']))) == res

    def test_getfiles_to_cut_static_setup(self):
        res = sorted(get_filelist(static_data_folder='tests/data/folder_a'))
        assert sorted(list(
            map(Path, ['tests/data/folder_a/1.map', 'tests/data/folder_a/2.map',
                       'tests/data/folder_a/3.map', 'tests/data/folder_a/4.map',
                       'tests/data/folder_a/5.map', 'tests/data/folder_a/qLakeIn.tss',
                       'tests/data/folder_a/test_tol_fail_1.tss', 'tests/data/folder_a/test_tol_ok_1.tss',
                       'tests/data/folder_a/qLakeOut.tss', 'tests/data/folder_a/ta.nc',
                       'tests/data/folder_a/tp.nc']))) == res

    def test_get_cuts_withcoords(self):
        # "lonmin lonmax latmin latmax"
        cuts = '-127.0 -126.5 53.2 53.4'
        cuts = get_arg_coords(cuts)
        x_min, x_max, y_min, y_max = get_cuts(cuts=cuts)
        assert (x_min, x_max, y_min, y_max) == (-127.0, -126.5, 53.2, 53.4)
        fin = 'tests/data/folder_a/ta.nc'
        fout = 'tests/data/folder_a/ta_cut.nc'
        self.cleanups.append((os.unlink, (fout,)))
        cutmap(fin, fout, x_min, x_max, y_min, y_max)
        with Dataset(fout) as nc:
            lons = nc.variables['lon'][:]
            lats = nc.variables['lat'][:]
            res_x_min = round(np.min(lons), 2)
            res_y_min = round(np.min(lats), 2)
            res_x_max = round(np.max(lons), 2)
            res_y_max = round(np.max(lats), 2)
        # ta.nc input file has not exact coordinates (e.g. there is no -127.0 in lons)
        assert (-126.95, -126.55, 53.25, 53.35) == (res_x_min, res_x_max, res_y_min, res_y_max)

    def test_get_cuts_indices(self):
        # "minxi maxxi minyi maxyi"
        cuts_indices = '3 7 1 2'
        cuts_indices = get_arg_coords(cuts_indices)
        ix_min, ix_max, iy_min, iy_max = get_cuts(cuts_indices=cuts_indices)
        assert (ix_min, ix_max, iy_min, iy_max) == (3, 7, 1, 2)
        fin = 'tests/data/folder_a/ta.nc'
        fout = 'tests/data/folder_a/ta_cut.nc'
        self.cleanups.append((os.unlink, (fout,)))
        cutmap(fin, fout, ix_min, ix_max, iy_min, iy_max, use_coords=False)
        with Dataset(fout) as nc:
            lons = nc.variables['lon'][:]
            lats = nc.variables['lat'][:]
            res_x_min = round(np.min(lons), 2)
            res_y_min = round(np.min(lats), 2)
            res_x_max = round(np.max(lons), 2)
            res_y_max = round(np.max(lats), 2)

        assert (-126.95, -126.55, 53.25, 53.35) == (res_x_min, res_x_max, res_y_min, res_y_max)

    def test_get_cuts_withmaskfile(self):
        maskfile = 'tests/data/masks/area.nc'
        x_min, x_max, y_min, y_max = get_cuts(mask=maskfile)
        x_minr, x_maxr, y_minr, y_maxr = np.round(x_min, 2), np.round(x_max, 2), np.round(y_min, 2), np.round(y_max, 2)
        assert (x_minr, x_maxr, y_minr, y_maxr) == (-127.25, -126.15, 53.05, 53.45)
        fin = 'tests/data/masks/world.nc'
        fout = 'tests/data/area_cut.nc'
        self.cleanups.append((os.unlink, (fout,)))
        cutmap(fin, fout, x_min, x_max, y_min, y_max)
        with Dataset(fout) as nc:
            lons = nc.variables['lon'][:]
            lats = nc.variables['lat'][:]
            res_x_min = np.min(lons)
            res_y_min = np.min(lats)
            res_x_max = np.max(lons)
            res_y_max = np.max(lats)

        assert (x_min, x_max, y_min, y_max) == (res_x_min, res_x_max, res_y_min, res_y_max)

    def test_get_cuts_withmaskfile_compare(self):
        maskfile = 'tests/data/submask/subcatchment_mask.map'
        x_min, x_max, y_min, y_max = get_cuts(mask=maskfile)
        assert (x_min, x_max, y_min, y_max) == (4052500.0, 4232500.0, 2332500.0, 2542500.0)
        fin = 'tests/data/submask/dis.nc'
        fout = 'tests/data/submask/dis_cut.nc'
        self.cleanups.append((os.unlink, (fout,)))
        cutmap(fin, fout, x_min, x_max, y_min, y_max)
        with Dataset(fout) as nc:
            lons = nc.variables['x'][:]
            lats = nc.variables['y'][:]
            res_x_min = np.min(lons)
            res_y_min = np.min(lats)
            res_x_max = np.max(lons)
            res_y_max = np.max(lats)
        assert (x_min, x_max, y_min, y_max) == (res_x_min, res_x_max, res_y_min, res_y_max)
        comparator = NetCDFComparator(array_equal=True)
        comparator.compare_files(fout, 'tests/data/submask/dis_subdomain.nc')
        comparator = NetCDFComparator(mask=maskfile, array_equal=True)
        comparator.compare_files(fin, fout)


    def test_get_cuts_withmaskpcr(self):
        maskfile = 'tests/data/masks/asia.map'
        x_min, x_max, y_min, y_max = get_cuts(mask=maskfile)
        x_minr, x_maxr, y_minr, y_maxr = np.round(x_min, 3), np.round(x_max, 3), np.round(y_min, 3), np.round(y_max, 3)
        assert (x_minr, x_maxr, y_minr, y_maxr) == (58.65, 179.95, 0.65, 81.25)
        fin = 'tests/data/masks/world.nc'
        fout = 'tests/data/area_cut.nc'
        self.cleanups.append((os.unlink, (fout,)))
        cutmap(fin, fout, x_min, x_max, y_min, y_max)
        with Dataset(fout) as nc:
            lons = nc.variables['lon'][:]
            lats = nc.variables['lat'][:]
            res_x_min = np.round(np.min(lons), 3)
            res_y_min = np.round(np.min(lats), 3)
            res_x_max = np.round(np.max(lons), 3)
            res_y_max = np.round(np.max(lats), 3)
        assert (x_minr, x_maxr, y_minr, y_maxr) == (res_x_min, res_x_max, res_y_min, res_y_max)

    def test_get_cuts_ldd(self):
        ldd_pcr = 'tests/data/cutmaps/ldd_eu.map'
        stations = 'tests/data/cutmaps/stations.txt'

        mask, outlets_points, mask_nc = mask_from_ldd(ldd_pcr, stations)
        self.cleanups.append((os.unlink, (mask,)))
        self.cleanups.append((os.unlink, (outlets_points,)))
        self.cleanups.append((os.unlink, (mask_nc,)))

        x_min, x_max, y_min, y_max = get_cuts(mask=mask)

        fin = 'tests/data/cutmaps/ldd_eu.nc'
        fout = 'tests/data/cutmaps/area_cut.nc'
        cutmap(fin, fout, x_min, x_max, y_min, y_max)
        self.cleanups.append((os.unlink, (fout,)))
        with Dataset(fout) as nc:
            lons = nc.variables['x'][:]
            lats = nc.variables['y'][:]
            res_x_min = np.min(lons)
            res_y_min = np.min(lats)
            res_x_max = np.max(lons)
            res_y_max = np.max(lats)
        assert (x_min, x_max, y_min, y_max) == (res_x_min, res_x_max, res_y_min, res_y_max)

    def test_get_cuts_ldd_onestation(self):
        # this tests the case when LDD is in netCDF format as well
        ldd = 'tests/data/cutmaps/ldd_eu.nc'
        stations = 'tests/data/cutmaps/stations2.txt'

        ldd_pcr_path = 'tests/data/cutmaps/ldd_eu_test.map'
        nc2pcr_convert(ldd, ldd_pcr_path, is_ldd=True)

        self.cleanups.append((os.unlink, (ldd_pcr_path,)))

        mask, outlets_points, mask_nc = mask_from_ldd(ldd_pcr_path, stations)
        self.cleanups.append((os.unlink, (mask,)))  # produced by mask_from_ldd
        self.cleanups.append((os.unlink, (outlets_points,)))  # produced by mask_from_ldd
        self.cleanups.append((os.unlink, (mask_nc,)))  # produced by mask_from_ldd
        x_min, x_max, y_min, y_max = get_cuts(mask=mask)
        assert (x_min, x_max, y_min, y_max) == (4347500.0, 4372500.0, 1282500.0, 1307500.0)

        fout = 'tests/data/cutmaps/ldd_eu_cut.nc'
        self.cleanups.append((os.unlink, (fout,)))
        cutmap(ldd, fout, x_min, x_max, y_min, y_max)

        with Dataset(fout) as nc:
            lons = nc.variables['x'][:]
            lats = nc.variables['y'][:]
            res_x_min = np.min(lons)
            res_y_min = np.min(lats)
            res_x_max = np.max(lons)
            res_y_max = np.max(lats)

        assert (x_min, x_max, y_min, y_max) == (res_x_min, res_x_max, res_y_min, res_y_max)
