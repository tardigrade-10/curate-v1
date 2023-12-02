import pytest
import asyncio
from core.features.htp.htp_class import HTPService
from core.features.utils import encode_image

# IDEAS
# fixture state from tests can affect further tests
# some issue with running async tests after sync tests so, run all async tests first and then sync tests
# instead of using fixture, use a global variable, or initialise the service in the test itself

# Fixture for the HTPService instance
@pytest.fixture
def htp_service():
    return HTPService()

# htp_service = HTPService()

# Test for asynchronous HTP processing
@pytest.mark.asyncio
async def test_async_htp_process(htp_service):
    test_image_paths = [r"tests\data\mmh_image2.jpg"]
    # , r"tests\data\image3.jpg"
    result, tokens, gpt_cost, serv_cost = await htp_service.async_htp_process(image_paths = test_image_paths, creator_args={"timeout": 60})
    assert isinstance(result, dict)
    assert isinstance(tokens, dict)
    assert isinstance(gpt_cost, dict)
    assert isinstance(serv_cost, float)


# Test for asynchronous HTP generation
@pytest.mark.asyncio
async def test_async_htp_gen(htp_service):
    test_image_base64 = encode_image(r"tests\data\mmh_image3.jpg")
    text, usage = await htp_service.async_htp_gen(test_image_base64)
    assert isinstance(text, dict)
    assert 'prompt_tokens' in usage


# Test for synchronous HTP generation
def test_htp_gen(htp_service):
    # Assuming you have a sample image encoded in base64 for testing
    test_image_base64 = encode_image(r"tests\data\mmh_image3.jpg")
    text, usage = htp_service.htp_gen(test_image_base64)
    assert isinstance(text, dict)
    assert 'prompt_tokens' in usage


# Test for HTP processing
def test_htp_process(htp_service):
    test_image_paths = [r"tests\data\mmh_image3.jpg", r"tests\data\image3.jpg"]
    result, tokens, gpt_cost, serv_cost = htp_service.htp_process(test_image_paths)
    assert isinstance(result, dict)
    assert isinstance(tokens, dict)
    assert isinstance(gpt_cost, dict)
    assert isinstance(serv_cost, float)

