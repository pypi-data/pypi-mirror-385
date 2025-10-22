NetTracer3D is a python package developed for both 2D and 3D analysis of microscopic images in the .tif file format. It supports generation of 3D networks showing the relationships between objects (or nodes) in three dimensional space, either based on their own proximity or connectivity via connecting objects such as nerves or blood vessels. In addition to these functionalities are several advanced 3D data processing algorithms, such as labeling of branched structures or abstraction of branched structures into networks. Note that nettracer3d uses segmented data, which can be segmented from other softwares such as ImageJ and imported into NetTracer3D, although it does offer its own segmentation via intensity and volumetric thresholding, or random forest machine learning segmentation. NetTracer3D currently has a fully functional GUI. To use the GUI, after installing the nettracer3d package via pip, enter the command 'nettracer3d' in your command prompt:

--- Documentation ---

Please see: https://nettracer3d.readthedocs.io/en/latest/

--- Installation ---

To install nettracer3d, simply install Python and use this command in your command terminal:

pip install nettracer3d

I recommend installing the program as an Anaconda package to ensure its modules are work together on your specific system:
(Install anaconda at the link below, set up a new python env for nettracer3d, then use the same pip command).

https://www.anaconda.com/download?utm_source=anacondadocs&utm_medium=documentation&utm_campaign=download&utm_content=installwindows

Optional Packages
~~~~~~~~~~~~~~~~~~
I recommend including Napari (Chi-Li Chiu, Nathan Clack, the napari community, napari: a Python Multi-Dimensional Image Viewer Platform for the Research Community, Microscopy and Microanalysis, Volume 28, Issue S1, 1 August 2022, Pages 1576–1577, https://doi.org/10.1017/S1431927622006328) in the download as well, which allows NetTracer3D to use 3D displays. The standard package only comes with its native 2D slice display window. 
If Napari is present, all 3D images and overlays from NetTracer3D can be easily displayed in 3D with a click of a button. To package with Napari, use this install command instead: 

    pip install nettracer3d[viz]

Additionally, for easy access to high-quality cell segmentation, as of version 0.8.2, NetTracer3D can be optionally packaged with Cellpose3. (Stringer, C., Pachitariu, M. Cellpose3: one-click image restoration for improved cellular segmentation. Nat Methods 22, 592–599 (2025). https://doi.org/10.1038/s41592-025-02595-5)
Cellpose3 is not involved with the rest of the program in any way, although its GUI can be opened from NetTracer3D's GUI, provided both are installed in the same environment. It is a top-tier cell segmenter which can assist in the production of cell networks.
To include Cellpose3 in the install, use this command:


    pip install nettracer3d[cellpose]

Alternatively, both Napari and Cellpose can be included in the package with this command: (Or they can be independently installed with pip from the base package env)


    pip install nettracer3d[all]

GPU
~~~~~~~~~~~~~~~~~~
NetTracer3D is mostly CPU-bound, but a few functions can optionally use the GPU. To install optional GPU functionalities, first set up a CUDA toolkit that runs with the GPU on your machine. This requires an NVIDIA GPU. Then, find your GPUs compatible CUDA toolkit and install it with the auto-installer from the NVIDIA website: https://developer.nvidia.com/cuda-toolkit

With a CUDA toolkit installed, use:

    pip install nettracer3d[CUDA11] #If your CUDA toolkit is version 11
    pip install nettracer3d[CUDA12] #If your CUDA toolkit is version 12
    pip install nettracer3d[cupy] #For the generic cupy library (The above two are usually the ones you want)

Or if you've already installed the NetTracer3D base package and want to get just the GPU associated packages:

    pip install cupy-cuda11x #If your CUDA toolkit is version 11
    pip install cupy-cuda12x #If your CUDA toolkit is version 12
    pip install cupy #For the generic cupy library (The above two are usually the ones you want)

While not related to NetTracer3D, if you want to use Cellpose3 (for which GPU-usage is somewhat obligatory) to help segment cells for any networks, you will also want to install pytorch here: https://pytorch.org/. Use the pytorch build menu on this webpage to find a pip install command that is compatible with Python and your CUDA version.


This gui is built from the PyQt6 package and therefore may not function on dockers or virtual envs that are unable to support PyQt6 displays.


For a (slightly outdated) video tutorial on using the GUI: https://www.youtube.com/watch?v=cRatn5VTWDY

NetTracer3D is free to use/fork for academic/nonprofit use so long as citation is provided, and is available for commercial use at a fee (see license file for information).
The current citation is here: 

McLaughlin, L., Zhang, B., Sharma, S. et al. Three dimensional multiscalar neurovascular nephron connectivity map of the human kidney across the lifespan. Nat Commun 16, 5161 (2025). https://doi.org/10.1038/s41467-025-60435-8

NetTracer3D was developed by Liam McLaughlin while working under Dr. Sanjay Jain at Washington University School of Medicine.

-- Version 1.1.1 Updates --

	* Can now intermittently downsample while making the network and id overlays now to make their relevant elements larger in the actual rendered output.