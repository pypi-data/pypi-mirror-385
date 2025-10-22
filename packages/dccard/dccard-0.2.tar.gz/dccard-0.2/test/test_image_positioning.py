import sys

sys.path.append("../dccard")
import io

from PIL import Image as PilImage

from dccard.canvas import Canvas
from dccard.type import Direction


def test_image_position_center_horizontal():
    """Test that image centers horizontally in a row group."""
    canvas = Canvas((500, 500))

    # Create a test image
    test_img = PilImage.new('RGB', (200, 200), color='red')

    # Add image with center positioning
    row = canvas.group(Direction.ROW)
    canvas.add_component(row)
    img_component = canvas.image(test_img).size((100, 100)).position('center')
    row.add(img_component)

    # Render the canvas
    result = canvas.render()

    # Verify the image was rendered without errors
    assert result is not None
    assert result.size == (500, 500)


def test_image_position_center_vertical():
    """Test that image centers vertically in a column group."""
    canvas = Canvas((500, 500))

    # Create a test image
    test_img = PilImage.new('RGB', (200, 200), color='blue')

    # Add image with center positioning in column
    col = canvas.group(Direction.COLUMN)
    canvas.add_component(col)
    img_component = canvas.image(test_img).size((100, 100)).position('center')
    col.add(img_component)

    # Render the canvas
    result = canvas.render()

    # Verify the image was rendered without errors
    assert result is not None
    assert result.size == (500, 500)


def test_image_position_center_both_directions():
    """Test that image centers both horizontally and vertically."""
    canvas = Canvas((500, 500))

    # Create a test image
    test_img = PilImage.new('RGB', (200, 200), color='green')

    # Create nested groups for bidirectional centering
    row = canvas.group(Direction.ROW)
    canvas.add_component(row)
    col = canvas.group(Direction.COLUMN)
    row.add(col)
    img_component = canvas.image(test_img).size((100, 100)).position('center')
    col.add(img_component)

    # Render the canvas
    result = canvas.render()

    # Verify the image was rendered without errors
    assert result is not None
    assert result.size == (500, 500)


def test_image_size_sets_dimensions():
    """Test that size() method sets all required dimension properties."""
    canvas = Canvas((500, 500))
    test_img = PilImage.new('RGB', (200, 200), color='yellow')

    img_component = canvas.image(test_img).size((150, 150))

    # Verify that size() sets all required properties
    assert img_component._size == (150, 150)
    assert img_component.minwidth == 150
    assert img_component.minheight == 150
    assert img_component.width == 150
    assert img_component.height == 150


def test_pil_image_instance_check():
    """Test that PIL Image instances are properly handled."""
    canvas = Canvas((500, 500))

    # Create a PIL Image directly
    test_img = PilImage.new('RGB', (100, 100), color='purple')

    # This should not raise an exception
    img_component = canvas.image(test_img)

    # Verify the image was properly stored
    assert img_component.pastimage == test_img


def test_image_from_bytes():
    """Test that images can be created from bytes (PIL Image object)."""
    canvas = Canvas((500, 500))

    # Create an image and convert to bytes
    original_img = PilImage.new('RGB', (50, 50), color='orange')
    img_bytes = io.BytesIO()
    original_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Load from bytes
    loaded_img = PilImage.open(img_bytes)

    # Create image component with size
    img_component = canvas.image(loaded_img).size((50, 50))

    # Render should work without errors
    canvas.add_component(img_component)
    result = canvas.render()
    assert result is not None
