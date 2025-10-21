import io
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import logging
from typing import Optional, Dict, Any, Callable, List
from PIL import Image
from utils.supabase_utils import upload_image_to_supabase

# Set matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Configure matplotlib to prevent memory leaks and limit figure accumulation
matplotlib.rcParams['figure.max_open_warning'] = 5  # Warn much earlier
matplotlib.rcParams['figure.raise_window'] = False   # Don't raise GUI windows

logger = logging.getLogger(__name__)


def plot_heatmap(
    data: List[List[float]],
    *,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    cmap: str = "viridis",
    annot: bool = False,
    fmt: str = ".2f",
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    colorbar: bool = True,
    legend_entries: Optional[List[Dict[str, str]]] = None,  # Added parameter
    background_color: str = 'transparent'
) -> str:
    """
    Draw a heatmap of a 2D array.

    Parameters
    ----------
    data : List[List[float]]
        2D array of numbers (list of lists).
    row_labels : List[str]
        Labels for each row (shown on the y-axis).
    col_labels : List[str]
        Labels for each column (shown on the x-axis).
    cmap : str"
        Name of the matplotlib colormap to use (e.g. 'viridis', 'plasma', 'coolwarm', 'RdYlBu').
    annot : bool
        If True, write the data value inside each cell.
    fmt : str
        Numeric format for annotations (only if annot=True).
    title : str
        Plot title.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    colorbar : bool
        Whether to show a color scale alongside the heatmap.
    legend_entries : List[Dict[str, str]]
        Optional list of legend entries. Each entry should be a dict with:
          - 'label': text to show in legend
          - 'color': color to show in legend (e.g. 'red', '#FF5733')
    background_color : str, default 'white'
        The background color behind the chart. Use 'transparent' for transparent background,
        or any valid matplotlib color name or hex code.
        
    Returns
    -------
    str
        URL of the generated image
    """
    try:
        # data is now already a 2D array, no need to parse JSON
        data_array = data
        print("Heatmap parameters:")
        print(f"Data shape: {np.array(data_array).shape}")
        print(f"Row labels: {row_labels}")
        print(f"Col labels: {col_labels}")
        print(f"Colormap: {cmap}")
        print(f"Annotations: {annot}")
        print(f"Format: {fmt}")
        print(f"Title: {title}")
        print(f"Xlabel: {xlabel}")
        print(f"Ylabel: {ylabel}")
        print(f"Colorbar: {colorbar}")
        print(f"Legend entries: {legend_entries}")  # Added print
        print(f"Background color: {background_color}")
        
        # row_labels and col_labels are now already lists, no need to parse JSON
        row_labels_list = row_labels
        col_labels_list = col_labels
        
        # Create figure with white background for the chart
        fig = plt.figure(figsize=(8, 6), facecolor='white')
        ax = fig.add_subplot(111, facecolor='white')
        
        # Create a white background patch that covers the entire chart area
        fig.patch.set_facecolor('white')
        
        mat = np.array(data_array)
        
        # Create heatmap
        im = ax.imshow(mat, cmap=cmap, aspect='auto')

        # Set axis labels
        if col_labels_list is not None:
            ax.set_xticks(np.arange(mat.shape[1]))
            ax.set_xticklabels(col_labels_list)
        if row_labels_list is not None:
            ax.set_yticks(np.arange(mat.shape[0]))
            ax.set_yticklabels(row_labels_list)

        # Rotate x-labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add annotations if requested
        if annot:
            for i in range(mat.shape[0]):
                for j in range(mat.shape[1]):
                    # Choose text color based on cell value for better visibility
                    text_color = 'black' if mat[i, j] < (mat.min() + mat.max()) / 2 else 'white'
                    ax.text(j, i, format(mat[i, j], fmt),
                            ha="center", va="center", color=text_color, fontweight='bold')

        # Set labels and title
        if title:
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20)  # Add some padding above title
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=18)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=18)

        # Add colorbar
        if colorbar:
            cbar = fig.colorbar(im, ax=ax)
            cbar.outline.set_edgecolor('black')
            cbar.outline.set_linewidth(1)
            # Set white background for colorbar
            cbar.ax.set_facecolor('white')

        # Add legend if entries are provided
        if legend_entries:
            legend_patches = []
            legend_labels = []
            for entry in legend_entries:
                patch = plt.Rectangle((0, 0), 1, 1, facecolor=entry['color'], edgecolor='black')
                legend_patches.append(patch)
                legend_labels.append(entry['label'])
            
            # Create legend
            legend = ax.legend(
                legend_patches,
                legend_labels,
                bbox_to_anchor=(0.5, -0.2),
                loc='upper center',
                ncol=min(len(legend_entries), 4)
            )
            # Set white background for legend
            if legend:
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_alpha(1.0)

        # Add grid for better cell separation
        ax.set_xticks(np.arange(mat.shape[1] + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(mat.shape[0] + 1) - 0.5, minor=True)
        ax.grid(which="minor", color="black", linestyle='-', linewidth=1, alpha=0.3)
        ax.tick_params(which="minor", size=0)

        # Ensure all spines are visible against any background
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')

        # Adjust layout
        plt.tight_layout()
        
        # Add extra space at bottom if legend is shown
        if legend_entries:
            plt.subplots_adjust(bottom=0.2)
        
        # Create a new figure with the specified background color for padding
        inner_pad_inches = 0.15  # White padding around the chart
        outer_pad_inches = 0.25  # Colored padding around the white padding
        
        # Save with white background and inner padding
        buf_white = io.BytesIO()
        fig.savefig(buf_white, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none',
                   pad_inches=inner_pad_inches)
        
        # Create new figure with specified background
        fig_with_bg = plt.figure(figsize=(8, 6))
        if background_color == 'transparent':
            fig_with_bg.patch.set_alpha(0)
        else:
            fig_with_bg.patch.set_facecolor(background_color)
        
        # Display the white-background image on this figure
        buf_white.seek(0)
        img = Image.open(buf_white)
        # Convert PIL Image to numpy array for matplotlib
        img_array = np.array(img)
        plt.imshow(img_array)
        plt.axis('off')
        
        # Save final version with outer padding
        buf_final = io.BytesIO()
        fig_with_bg.savefig(buf_final, format='png', dpi=300, bbox_inches='tight',
                   transparent=(background_color == 'transparent'),
                   pad_inches=outer_pad_inches)
        buf_final.seek(0)
        
        # Clean up the first buffer
        buf_white.close()
        
        # Upload to Supabase
        public_url = upload_image_to_supabase(
            image_bytes=buf_final.getvalue(),
            content_type="image/png",
            bucket_name="incept-images",
            file_extension=".png"
        )
        
        # Thread-safe cleanup - close specific figures only
        plt.close(fig)
        plt.close(fig_with_bg)
        buf_final.close()
        
        return public_url
        
    except Exception as e:
        error_message = f"Error generating heatmap: {str(e)}"
        logger.error(error_message)
        # Ensure cleanup on error - close any figures we may have created
        try:
            if 'fig' in locals():
                plt.close(fig)
        except Exception:
            pass
        try:
            if 'fig_with_bg' in locals():
                plt.close(fig_with_bg)
        except Exception:
            pass
        raise RuntimeError(error_message)


def generate_simple_heatmap_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the simple heatmap tool specification and function."""
    
    spec = {
        "type": "function",
        "name": "plot_heatmap",
        "description": "Create a heatmap to visualize 2D data matrices. Colors represent data values in a grid format.",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "2D array of numbers (list of lists)",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Row of numeric values"
                    }
                },
                "row_labels": {
                    "type": "array",
                    "description": "Labels for each row (y-axis)",
                    "items": {"type": "string"}
                },
                "col_labels": {
                    "type": "array",
                    "description": "Labels for each column (x-axis)",
                    "items": {"type": "string"}
                },
                "cmap": {
                    "type": "string",
                    "description": "Colormap name. Popular options: 'viridis' (purple-blue-green), 'plasma' (purple-pink-yellow), 'coolwarm' (blue-white-red), 'RdYlBu' (red-yellow-blue), 'Blues', 'Reds', 'Greens'."
                },
                "annot": {
                    "type": "boolean",
                    "description": "Whether to display the actual values as text inside each cell."
                },
                "fmt": {
                    "type": "string",
                    "description": "Number format for annotations (only used if annot=true). Use '.2f' (2 decimals), '.1f' (1 decimal), '.0f' (whole numbers), 'd' (integers)."
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "xlabel": {
                    "type": "string",
                    "description": "Label for x-axis (columns)"
                },
                "ylabel": {
                    "type": "string",
                    "description": "Label for y-axis (rows)"
                },
                "colorbar": {
                    "type": "boolean",
                    "description": "Whether to show the color scale bar."
                },
                "legend_entries": {
                    "type": "array",
                    "description": "Optional list of legend entries to show below the heatmap",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Text to show in legend"
                            },
                            "color": {
                                "type": "string",
                                "description": "Color to show in legend (e.g. 'red', '#FF5733')"
                            }
                        },
                        "required": ["label", "color"]
                    }
                },
                "background_color": {
                    "type": "string",
                    "description": "The background color behind the chart. Use 'transparent' for transparent background, or any valid matplotlib color name or hex code. Defaults to 'transparent'."
                }
            },
            "required": ["data", "row_labels", "col_labels", "cmap", "annot", "fmt", "title", "xlabel", "ylabel", "colorbar", "legend_entries", "background_color"]
        }
    }
    
    return spec, plot_heatmap 