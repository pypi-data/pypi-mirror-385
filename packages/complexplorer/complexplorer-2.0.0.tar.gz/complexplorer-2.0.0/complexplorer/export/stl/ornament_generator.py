"""STL ornament generator for complex functions.

This module generates 3D-printable ornaments from complex functions
by using the modulus-scaled Riemann sphere mesh with optional simple repairs.
"""

import os
import numpy as np
import warnings
from typing import Callable, Optional, Dict, Any

from complexplorer.core.colormap import Colormap, Phase
from complexplorer.core.domain import Domain
from complexplorer.utils.validation import ValidationError
from complexplorer.utils.mesh import RectangularSphereGenerator
from complexplorer.utils.mesh_distortion import (
    compute_riemann_sphere_distortion,
    get_default_scaling_params
)
from complexplorer.export.stl.utils import check_pyvista_available, validate_printability, scale_to_size, center_mesh
from complexplorer.export.stl.mesh_repair import repair_mesh_simple

# Import PyVista if available
try:
    import pyvista as pv
    HAS_PYVISTA = True
except ImportError:
    HAS_PYVISTA = False
    pv = None


class OrnamentGenerator:
    """Generate 3D-printable ornaments from complex functions.

    This version directly uses the modulus-scaled mesh from the
    Riemann sphere visualization without complex healing steps.

    Parameters
    ----------
    func : callable
        Complex function f(z) to visualize.
    resolution : int, default=150
        Mesh resolution (n_theta = n_phi).
    modulus_mode : str, default='arctan'
        Modulus scaling method: 'constant', 'linear', 'arctan',
        'logarithmic', 'linear_clamp', 'power', 'sigmoid', 'adaptive',
        'hybrid', or 'custom'.
    modulus_params : dict, optional
        Parameters for scaling method. If None, uses STL-appropriate defaults.
    cmap : Colormap, optional
        Colormap for visualization. Default is Phase colormap.
    domain : Domain, optional
        Domain to restrict evaluation. Helps avoid numerical issues.

    Notes
    -----
    The deprecated parameters `scaling` and `scaling_params` are still supported
    for backwards compatibility but will emit deprecation warnings.
    """
    
    def __init__(self,
                 func: Callable,
                 resolution: int = 150,
                 modulus_mode: str = 'arctan',
                 modulus_params: Optional[Dict[str, Any]] = None,
                 cmap: Optional[Colormap] = None,
                 domain: Optional[Domain] = None,
                 # Deprecated parameters (for backwards compatibility)
                 scaling: Optional[str] = None,
                 scaling_params: Optional[Dict[str, Any]] = None):
        """Initialize ornament generator.

        Parameters
        ----------
        func : callable
            Complex function f(z) to visualize.
        resolution : int, default=150
            Mesh resolution (n_theta = n_phi).
        modulus_mode : str, default='arctan'
            Modulus scaling method: 'constant', 'linear', 'arctan',
            'logarithmic', 'linear_clamp', 'power', 'sigmoid', 'adaptive',
            'hybrid', or 'custom'.
        modulus_params : dict, optional
            Parameters for scaling method. If None, uses STL-appropriate defaults.
        cmap : Colormap, optional
            Colormap for visualization. Default is Phase colormap.
        domain : Domain, optional
            Domain to restrict evaluation. Helps avoid numerical issues.
        scaling : str, optional
            DEPRECATED. Use `modulus_mode` instead.
        scaling_params : dict, optional
            DEPRECATED. Use `modulus_params` instead.
        """
        check_pyvista_available()

        # Handle deprecated parameter names
        if scaling is not None:
            warnings.warn(
                "Parameter 'scaling' is deprecated and will be removed in a future version. "
                "Use 'modulus_mode' instead.",
                DeprecationWarning,
                stacklevel=2
            )
            modulus_mode = scaling

        if scaling_params is not None:
            warnings.warn(
                "Parameter 'scaling_params' is deprecated and will be removed in a future version. "
                "Use 'modulus_params' instead.",
                DeprecationWarning,
                stacklevel=2
            )
            modulus_params = scaling_params

        self.func = func
        self.resolution = resolution
        self.modulus_mode = modulus_mode
        self.modulus_params = modulus_params or get_default_scaling_params(modulus_mode, for_stl=True)
        self.cmap = cmap or Phase(phase_sectors=6, auto_scale_r=True)
        self.domain = domain

        self.sphere_mesh = None
    
    def generate_ornament(self, verbose: bool = False) -> 'pv.PolyData':
        """Generate the ornament mesh.
        
        Parameters
        ----------
        verbose : bool, optional
            Print progress information.
            
        Returns
        -------
        pv.PolyData
            Generated ornament mesh with color information.
        """
        if verbose:
            print(f"Generating Riemann sphere ornament:")
            print(f"  Resolution: {self.resolution}")
            print(f"  Modulus scaling: {self.modulus_mode}")
            print(f"  Parameters: {self.modulus_params}")
        
        # Generate base sphere
        generator = RectangularSphereGenerator(
            radius=1.0,
            n_theta=self.resolution,
            n_phi=self.resolution,
            avoid_poles=True,
            domain=self.domain
        )
        sphere = generator.generate()
        
        # Compute distortion
        scaled_points, f_vals, radii = compute_riemann_sphere_distortion(
            sphere,
            self.func,
            self.modulus_mode,
            self.modulus_params,
            from_north=True
        )
        
        # Update mesh
        sphere.points = scaled_points
        
        # Add colors
        if self.domain is None:
            # Regular grid - can reshape
            f_vals_reshaped = f_vals.reshape((self.resolution, self.resolution))
            rgb = self.cmap.rgb(f_vals_reshaped)
            rgb_flat = rgb.reshape(-1, 3)
        else:
            # Irregular points due to domain filtering
            if f_vals.ndim == 1:
                f_vals_2d = f_vals.reshape(-1, 1)
            else:
                f_vals_2d = f_vals
            rgb = self.cmap.rgb(f_vals_2d)
            if rgb.ndim == 3 and rgb.shape[2] == 3:
                rgb_flat = rgb.reshape(-1, 3)
            else:
                rgb_flat = rgb.squeeze()
        
        sphere["RGB"] = rgb_flat
        sphere["magnitude"] = np.abs(f_vals)
        sphere["phase"] = np.angle(f_vals)
        sphere["radius"] = radii
        
        self.sphere_mesh = sphere
        
        if verbose:
            print(f"  Generated mesh: {sphere.n_points} vertices, {sphere.n_cells} faces")
            actual_radii = np.linalg.norm(sphere.points, axis=1)
            print(f"  Radius range: [{actual_radii.min():.3f}, {actual_radii.max():.3f}]")
        
        return sphere
    
    def validate_mesh(self, size_mm: float = 50, verbose: bool = True) -> Dict[str, Any]:
        """Validate mesh for 3D printing.
        
        Parameters
        ----------
        size_mm : float, default=50
            Target size in millimeters.
        verbose : bool, default=True
            Print validation results.
            
        Returns
        -------
        dict
            Validation results.
        """
        if self.sphere_mesh is None:
            raise ValueError("No mesh generated yet. Call generate_ornament() first.")
        
        return validate_printability(self.sphere_mesh, size_mm, verbose)
    
    def save_stl(self,
                 filename: str,
                 size_mm: float = 50,
                 center: bool = True,
                 repair: bool = True,
                 binary: bool = True,
                 validate: bool = True,
                 verbose: bool = True) -> str:
        """Save the ornament as STL file.
        
        Parameters
        ----------
        filename : str
            Output filename (should end with .stl).
        size_mm : float, default=50
            Scale mesh to this size in millimeters.
        center : bool, default=True
            Center the mesh at origin.
        repair : bool, default=True
            Apply simple mesh repair (fill holes).
        binary : bool, default=True
            Save as binary STL (smaller file size).
        validate : bool, default=True
            Validate before saving.
        verbose : bool, default=True
            Print progress information.
            
        Returns
        -------
        str
            Path to saved file.
        """
        if self.sphere_mesh is None:
            raise ValueError("No mesh generated yet. Call generate_ornament() first.")
        
        mesh = self.sphere_mesh.copy()
        
        # Repair if requested
        if repair:
            if verbose:
                print("\nRepairing mesh...")
            mesh = repair_mesh_simple(mesh, fill_holes=True, verbose=verbose)
        
        # Center if requested
        if center:
            mesh = center_mesh(mesh)
        
        # Scale to target size
        mesh = scale_to_size(mesh, size_mm, axis='max')
        
        # Validate if requested
        if validate:
            results = validate_printability(mesh, size_mm, verbose=verbose)
            if not results['is_watertight'] and not repair:
                warnings.warn("Mesh is not watertight. Consider enabling repair=True.")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Save
        mesh.save(filename, binary=binary)
        
        if verbose:
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            print(f"\nSaved STL file: {filename}")
            print(f"File size: {file_size_mb:.2f} MB")
        
        return filename
    
    def generate_and_save(self,
                         filename: str,
                         size_mm: float = 50,
                         center: bool = True,
                         repair: bool = True,
                         binary: bool = True,
                         validate: bool = True,
                         verbose: bool = True) -> str:
        """Generate ornament and save as STL in one step.
        
        Parameters
        ----------
        filename : str
            Output filename.
        size_mm : float, default=50
            Target size in millimeters.
        center : bool, default=True
            Center the mesh.
        repair : bool, default=True
            Apply simple mesh repair.
        binary : bool, default=True
            Use binary STL format.
        validate : bool, default=True
            Validate before saving.
        verbose : bool, default=True
            Print progress.
            
        Returns
        -------
        str
            Path to saved file.
        """
        self.generate_ornament(verbose=verbose)
        return self.save_stl(filename, size_mm, center, repair, binary, validate, verbose)


def create_ornament(func: Callable,
                      filename: str,
                      size_mm: float = 50,
                      resolution: int = 150,
                      modulus_mode: str = 'arctan',
                      modulus_params: Optional[Dict[str, Any]] = None,
                      cmap: Optional[Colormap] = None,
                      domain: Optional[Domain] = None,
                      verbose: bool = True,
                      # Deprecated parameters
                      scaling: Optional[str] = None,
                      scaling_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a 3D-printable ornament from a complex function.

    Convenience function for creating STL files from complex functions.

    Parameters
    ----------
    func : callable
        Complex function to visualize.
    filename : str
        Output STL filename.
    size_mm : float, default=50
        Size in millimeters.
    resolution : int, default=150
        Mesh resolution.
    modulus_mode : str, default='arctan'
        Modulus scaling method: 'constant', 'linear', 'arctan',
        'logarithmic', 'linear_clamp', 'power', 'sigmoid', 'adaptive',
        'hybrid', or 'custom'.
    modulus_params : dict, optional
        Scaling parameters.
    cmap : Colormap, optional
        Color mapping.
    domain : Domain, optional
        Domain restriction.
    verbose : bool, default=True
        Print progress.
    scaling : str, optional
        DEPRECATED. Use `modulus_mode` instead.
    scaling_params : dict, optional
        DEPRECATED. Use `modulus_params` instead.

    Returns
    -------
    str
        Path to saved STL file.
    """
    # Handle deprecated parameters
    if scaling is not None:
        warnings.warn(
            "Parameter 'scaling' is deprecated and will be removed in a future version. "
            "Use 'modulus_mode' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        modulus_mode = scaling

    if scaling_params is not None:
        warnings.warn(
            "Parameter 'scaling_params' is deprecated and will be removed in a future version. "
            "Use 'modulus_params' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        modulus_params = scaling_params

    gen = OrnamentGenerator(
        func, resolution, modulus_mode, modulus_params, cmap, domain
    )
    return gen.generate_and_save(filename, size_mm, verbose=verbose)


__all__ = ['OrnamentGenerator', 'create_ornament']