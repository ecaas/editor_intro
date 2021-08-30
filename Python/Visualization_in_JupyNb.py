# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# ## Visualization in jupyter notebook
# ### Reading in the data:
#
# - We use `xarray` here, but you can also use e.g. iris or even pyaerocom!
# - We recomend however, that you use a package that keeps track of your coordinates in your data and the metadata in your data! (E.g. numpy doesn't do this)
# - This is also why the NetCDF format is so popular -- it keeps track of these things and is extremely easy to load with these packages.
#

# %%
# supress warnings
import warnings

warnings.filterwarnings("ignore")  # don't output warnings

# import packages
from imports import np, plt, xr

# reload imports
get_ipython().run_line_magic("load_ext", "autoreload")
get_ipython().run_line_magic("autoreload", "2")


# %%
# Load data
file = "./wrf_out.small.h5"
ds = xr.open_dataset(file)


# %%
# Check how the dataset looks like
ds


# %%
# Check the attributes
ds.XTIME


# %%
# Assign attributes and process potential temperature into degC.
# Nice for plotting and to keep track of what is in your dataset (especially 'units' and 'standard_name'/'long_name' will be looked for by xarray.

ds["T_C"] = ds["T"] + 300 - 273
ds["T_C"] = ds["T_C"].assign_attrs({"units": "C"})
ds["T_C"] = ds["T_C"].assign_attrs({"description": "Temperature in C"})


# %%
# Check for attributes
ds.T_C.attrs


# %%
# Basic plot of potential temperature in degC
_t_c = ds.T_C.isel(XTIME=0, bottom_top=0)
_t_c.plot()


# %%
# Change the coordinate 'south_north' to latitude!
ds["south_north"] = ds.XLAT[:, 0]
ds["west_east"] = ds.XLONG[0, :]

# Reanme the coordinates
ds = ds.rename({"south_north": "lat", "west_east": "lon"})


# %%
# lets define some constants for the variable names so that calling them is easier.
ilev = "bottom_top"
lat = "lat"
lon = "lon"
XT = "XTIME"
time = "XTIME"
P, V, U, T = "P", "V", "U", "T"

# this is potential temperature in C
T_C = "T_C"


# %%
# create new variable
WS = "Wind speed"

ds[WS] = np.sqrt(ds[U] ** 2 + ds[V] ** 2)

ds[WS].attrs["units"] = "m/s"
ds[WS].attrs["long_name"] = "Wind SPEED"

# %% [markdown]
# # Plotting

# %%
from imports import cy, ccrs


# %%


# %%
f, ax = plt.subplots(nrows=1, ncols=1, subplot_kw={"projection": ccrs.PlateCarree()})
_ds = ds[{ilev: 0}]
_dm = _ds[WS].mean([time])

_dm.plot.pcolormesh(
    cmap=plt.get_cmap("Reds"), ax=ax, transform=ccrs.PlateCarree(), levels=6,
)

ax.set_title("BT:0; Mean over Time")
ax.coastlines()

gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
ax.add_feature(cy.feature.BORDERS)


# %%
# Making map features
def sp_map(*nrs, projection=ccrs.PlateCarree(), **kwargs):
    return plt.subplots(*nrs, subplot_kw={"projection": projection}, **kwargs)


def add_map_features(ax):
    ax.coastlines()
    gl = ax.gridlines()
    ax.add_feature(cy.feature.BORDERS)
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = False
    gl.ylabels_right = False


# %%
# Some quick statistics
fig, axsm = sp_map(2, 2, figsize=[10, 7],)
axs = axsm.flatten()
_ds = ds[T_C][{ilev: 0}]
_ds.mean(time, keep_attrs=True).plot(
    ax=axs[0], transform=ccrs.PlateCarree(), robust=True
)
axs[0].set_title("Mean")
_ds.std(time, keep_attrs=True).plot(
    ax=axs[1], transform=ccrs.PlateCarree()
)  # , robust=True)
axs[1].set_title("Std")
_ds.quantile(0.05, dim=time, keep_attrs=True).plot(
    ax=axs[2], transform=ccrs.PlateCarree()
)  # , robust=True)
_ds.quantile(0.95, dim=time, keep_attrs=True).plot(
    ax=axs[3], transform=ccrs.PlateCarree()
)  # , robust=True)
for ax in axs:
    add_map_features(ax)

plt.tight_layout()


# %%

