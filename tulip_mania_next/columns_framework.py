from IPython.display import display, HTML
import uuid
from typing import Union, List, Optional
import base64
from io import BytesIO


class Column:
    """
    A container for HTML content that represents a single column.
    Similar to Streamlit's column object.
    """

    def __init__(self, column_id: str, width_ratio: float):
        self.column_id = column_id
        self.width_ratio = width_ratio
        self.content = []

    def write(self, content: str, tag: str = "p", **kwargs):
        """Add text content to the column."""
        style = kwargs.get("style", "")
        classes = kwargs.get("class", "")
        html = f'<{tag} class="{classes}" style="{style}">{content}</{tag}>'
        self.content.append(html)

    def markdown(self, content: str):
        """Add markdown-style content (simplified)."""
        # Simple markdown conversion (you could use markdown library for full support)
        content = content.replace("**", "<strong>").replace("**", "</strong>")
        content = content.replace("*", "<em>").replace("*", "</em>")
        self.write(content)

    def header(self, content: str, level: int = 2):
        """Add a header to the column."""
        self.write(content, tag=f"h{level}")

    def image(self, src: str, alt: str = "", width: str = "100%"):
        """Add an image to the column."""
        html = f'<img src="{src}" alt="{alt}" style="width: {width}; height: auto;">'
        self.content.append(html)

    def html(self, html_content: str):
        """Add raw HTML content to the column."""
        self.content.append(html_content)

    def plot(self, figure, **kwargs):
        """
        Add a plot to the column. Automatically detects whether it's a Plotly or Matplotlib figure.

        Parameters:
        -----------
        figure : plotly.graph_objects.Figure or matplotlib.figure.Figure
            The figure to display
        **kwargs : Additional arguments passed to the appropriate method (plotly or matplotlib)
        """
        if figure is None:
            return

        # Check if it's a Plotly figure
        if hasattr(figure, "to_html"):
            self.plotly(figure, **kwargs)
        # Check if it's a Matplotlib figure
        elif hasattr(figure, "savefig"):
            self.matplotlib(figure, **kwargs)
        else:
            raise ValueError("Figure must be either a Plotly or Matplotlib figure")

    def plotly(
        self, figure, config: Optional[dict] = None, include_plotlyjs: str = "cdn"
    ):
        """Add a Plotly figure to the column with responsive behaviour."""
        if figure is None:
            return

        default_config = {
            "responsive": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        }
        merged_config = {**default_config, **(config or {})}

        # Ensure the figure has autosize enabled for better responsiveness
        if hasattr(figure, "update_layout"):
            figure.update_layout(
                autosize=True,
                # Remove fixed width/height if they exist
                width=None,
                height=None,
            )

        html = figure.to_html(
            include_plotlyjs=include_plotlyjs, full_html=False, config=merged_config
        )
        responsive_html = f'<div style="width: 100%; min-height: 400px; overflow: hidden;">{html}</div>'
        self.content.append(responsive_html)

    def matplotlib(
        self,
        figure,
        format: str = "png",
        dpi: int = 150,
        bbox_inches: str = "tight",
        **kwargs,
    ):
        """
        Add a Matplotlib figure to the column as an embedded image.

        Parameters:
        -----------
        figure : matplotlib.figure.Figure
            The matplotlib figure to display
        format : str, default 'png'
            Image format ('png', 'jpg', 'svg')
        dpi : int, default 100
            Dots per inch for the image
        bbox_inches : str, default 'tight'
            Bounding box setting for the figure
        **kwargs : Additional arguments passed to savefig
        """
        if figure is None:
            return

        # Save figure to BytesIO buffer
        buffer = BytesIO()
        figure.savefig(
            buffer, format=format, dpi=dpi, bbox_inches=bbox_inches, **kwargs
        )
        buffer.seek(0)

        # Encode to base64
        if format == "svg":
            # For SVG, embed directly as text
            svg_data = buffer.read().decode("utf-8")
            html = f'<div style="width: 100%; text-align: center;">{svg_data}</div>'
        else:
            # For raster images, use base64 encoding
            image_data = base64.b64encode(buffer.read()).decode("utf-8")
            mime_type = "image/jpeg" if format in ["jpg", "jpeg"] else f"image/{format}"
            html = f'<img src="data:{mime_type};base64,{image_data}" style="width: 100%; height: auto; display: block; margin: 0 auto;">'

        self.content.append(html)
        buffer.close()

    def table(self, data: List[List], headers: Optional[List] = None):
        """Add a simple HTML table to the column."""
        html = '<table style="width: 100%; border-collapse: collapse;">'

        if headers:
            html += "<thead><tr>"
            for header in headers:
                html += f'<th style="border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">{header}</th>'
            html += "</tr></thead>"

        html += "<tbody>"
        for row in data:
            html += "<tr>"
            for cell in row:
                html += f'<td style="border: 1px solid #ddd; padding: 8px;">{cell}</td>'
            html += "</tr>"
        html += "</tbody></table>"

        self.content.append(html)

    def _get_html(self) -> str:
        """Get the HTML representation of the column."""
        return "".join(self.content)


class ColumnsContainer:
    """
    A container that manages multiple columns and renders them as HTML.
    """

    def __init__(
        self,
        columns: List[Column],
        gap: str = "20px",
        vertical_alignment: str = "top",
        border: bool = False,
    ):
        self.columns = columns
        self.gap = gap
        self.vertical_alignment = vertical_alignment
        self.border = border
        self.container_id = f"columns-{uuid.uuid4().hex[:8]}"

    def render(self):
        """Render the columns as HTML in Jupyter notebook."""
        # Calculate flex values based on width ratios
        total_ratio = sum(col.width_ratio for col in self.columns)
        num_columns = len(self.columns)

        # Build CSS with enhanced responsive breakpoints
        css = f"""
        <style>
            #{self.container_id} {{
                display: flex;
                gap: {self.gap};
                align-items: {self._get_alignment()};
                width: 100%;
                margin: 10px 0;
            }}

            #{self.container_id} .column {{
                padding: 10px;
                {"border: 1px solid #e0e0e0; border-radius: 4px;" if self.border else ""}
                min-width: 0; /* Prevent flex items from overflowing */
            }}

            /* Ensure images and figures within columns are responsive */
            #{self.container_id} img {{
                max-width: 100%;
                height: auto;
            }}

            #{self.container_id} .plotly-graph-div {{
                width: 100% !important;
            }}

            /* Responsive breakpoints */

            /* Large screens (>1400px) - Keep side by side */
            @media (min-width: 1400px) {{
                #{self.container_id} {{
                    gap: {self.gap};
                }}
            }}

            /* Medium-large screens (1024px - 1399px) - Stack if 3+ columns */
            @media (min-width: 1024px) and (max-width: 1399px) {{
                #{self.container_id} {{
                    gap: calc({self.gap} * 0.75); /* Slightly smaller gap */
                }}

                /* Stack columns if 3 or more */
                {"#{self.container_id} { flex-direction: column; }" if num_columns >= 3 else ""}
                {"#{self.container_id} .column { flex: 1 1 100% !important; }" if num_columns >= 3 else ""}
            }}

            /* Small screens (768px - 1023px) - Stack if 2+ columns */
            @media (min-width: 768px) and (max-width: 1023px) {{
                #{self.container_id} {{
                    flex-direction: column;
                    gap: calc({self.gap} * 0.5);
                }}
                #{self.container_id} .column {{
                    flex: 1 1 100% !important;
                }}
            }}

            /* Mobile (<768px) - Always stack */
            @media (max-width: 767px) {{
                #{self.container_id} {{
                    flex-direction: column;
                    gap: 1rem;
                }}
                #{self.container_id} .column {{
                    flex: 1 1 100% !important;
                    padding: 8px;
                }}
            }}
        </style>
        """

        # Build HTML
        html = f'<div id="{self.container_id}">'

        for col in self.columns:
            flex_value = col.width_ratio / total_ratio
            column_style = f"flex: {flex_value} 1 0;"
            html += f'<div class="column" style="{column_style}">'
            html += col._get_html()
            html += "</div>"

        html += "</div>"

        # Display in Jupyter
        display(HTML(css + html))

    def _get_alignment(self) -> str:
        """Convert alignment parameter to CSS align-items value."""
        alignment_map = {"top": "flex-start", "center": "center", "bottom": "flex-end"}
        return alignment_map.get(self.vertical_alignment, "flex-start")


def columns(
    spec: Union[int, List[Union[int, float]]],
    gap: str = "20px",
    vertical_alignment: str = "top",
    border: bool = False,
) -> Union[List[Column], Column]:
    """
    Create columns for layout in Jupyter notebook, similar to Streamlit's st.columns.

    Parameters:
    -----------
    spec : int or list of numbers
        - If int: number of columns of equal width
        - If list: relative width ratios for each column (e.g., [3, 1] for 3:1 ratio)

    gap : str, default "20px"
        Gap between columns (CSS value like "20px", "2em", etc.)

    vertical_alignment : str, default "top"
        Vertical alignment of columns ("top", "center", "bottom")

    border : bool, default False
        Whether to add borders around columns

    Returns:
    --------
    List[Column] or Column
        Column object(s) that can be used to add content

    Examples:
    ---------
    # Create 3 equal columns
    col1, col2, col3 = columns(3)
    col1.header("First Column")
    col1.write("This is content in the first column")
    col2.header("Second Column")
    col2.write("This is content in the second column")
    col3.header("Third Column")
    col3.write("This is content in the third column")

    # Create columns with specific ratios
    left, right = columns([3, 1])
    left.header("Wide column")
    left.write("This takes up 3/4 of the width")
    right.header("Narrow column")
    right.write("This takes up 1/4 of the width")

    # Use with context manager style
    cols = columns(2, border=True)
    with cols:
        cols[0].header("Left")
        cols[0].write("Left content")
        cols[1].header("Right")
        cols[1].write("Right content")
    """

    # Parse spec into width ratios
    if isinstance(spec, int):
        # Equal width columns
        width_ratios = [1.0] * spec
    elif isinstance(spec, list):
        # Custom width ratios
        width_ratios = [float(x) for x in spec]
    else:
        raise ValueError("spec must be an int or a list of numbers")

    # Create column objects
    column_objects = []
    for i, ratio in enumerate(width_ratios):
        column_id = f"col-{uuid.uuid4().hex[:8]}"
        column_objects.append(Column(column_id, ratio))

    # Create container
    container = ColumnsContainer(column_objects, gap, vertical_alignment, border)

    # Add render method to the list
    class ColumnsList(list):
        def __init__(self, items, container):
            super().__init__(items)
            self.container = container

        def render(self):
            """Render the columns."""
            self.container.render()

        def __enter__(self):
            """Context manager support."""
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Auto-render when exiting context."""
            self.render()

    result = ColumnsList(column_objects, container)

    # Return unpacked if single column, otherwise return list
    if len(result) == 1:
        return result[0]
    return result


def render_columns(*column_objects):
    """
    Helper function to render multiple column objects at once.

    Parameters:
    -----------
    *column_objects : Column objects
        Column objects to render

    Example:
    --------
    col1, col2 = columns(2)
    col1.write("First column")
    col2.write("Second column")
    render_columns(col1, col2)
    """
    if not column_objects:
        return

    # Extract the container from the first column (all share same container)
    if hasattr(column_objects, "container"):
        column_objects.container.render()
    else:
        # Create a new container for these columns
        container = ColumnsContainer(list(column_objects))
        container.render()


if __name__ == "__main__":
    # Example usage
    cols = columns([2, 1], gap="30px", vertical_alignment="center", border=True)
    with cols:
        cols[0].header("Left Column")
        cols[0].write("Using context manager style")
        cols[0].html("<button style='padding: 10px;'>Click me</button>")

        cols[1].header("Right Column")
        cols[1].write("Content is automatically rendered when exiting the context")
        cols[1].image("https://via.placeholder.com/200x100")
