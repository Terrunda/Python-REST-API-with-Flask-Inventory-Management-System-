import pytest
from _pytest.capture import CaptureFixture
from unittest.mock import patch, MagicMock
import requests

from cli import (
    view_all_items,
    view_item_by_id,
    add_item,
    update_item,
    delete_item,
    find_on_api,
    BASE_URL
)


def mock_response(status_code, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
    else:
        mock.raise_for_status.return_value = None
    return mock


""" Tests for view_all_items function."""
@patch('cli.requests.get')
def test_view_all_items_success(mock_get, capsys: CaptureFixture[str]):

    mock_get.return_value = mock_response(200, [
        {"id": 1, "name": "Apple", "price": 1.5, "stock": 100}
    ])

    view_all_items()
    
    mock_get.assert_called_once_with(f"{BASE_URL}/inventory")
    captured = capsys.readouterr()
    assert "ID: 1 | Name: Apple | Price: $1.5 | Stock: 100" in captured.out


@patch('cli.requests.get')
def test_view_all_items_empty(mock_get, capsys: CaptureFixture[str]):
    mock_get.return_value = mock_response(200, [])
    view_all_items()
    captured = capsys.readouterr()
    assert "Inventory is empty" in captured.out


"""Tests for view_item_by_id function"""
@patch('cli.requests.get')
@patch('builtins.input', return_value='1') # This tests when the user types 1 to search for an item with an id of 1.
def test_view_item_by_id_success(mock_input, mock_get, capsys: CaptureFixture[str]):
    mock_get.return_value = mock_response(200, {
        "id": 1, "name": "Banana", "price": 0.5, "stock": 50
    })

    view_item_by_id()

    mock_get.assert_called_once_with(f"{BASE_URL}/inventory/1")
    captured = capsys.readouterr()
    assert "ID: 1 | Name: Banana" in captured.out


@patch('cli.requests.get')
@patch('builtins.input', return_value='999')
def test_view_item_by_id_not_found(mock_input, mock_get, capsys: CaptureFixture[str]):
    mock_get.return_value = mock_response(404)

    view_item_by_id()

    captured = capsys.readouterr()
    assert "Item with ID 999 not found" in captured.out


"""Tests the add_item function """
@patch('cli.requests.post')
@patch('builtins.input', side_effect=['y', '12345', 'Orange', '2.0', '30']) 
def test_add_item_success(mock_input, mock_post, capsys: CaptureFixture[str]):
    mock_post.return_value = mock_response(201)

    add_item()

    # Verifies the request payload sent to Flask
    mock_post.assert_called_once_with(
        f"{BASE_URL}/inventory", 
        json={"name": "Orange", "price": 2.0, "stock": 30, "barcode": "12345"}
    )
    captured = capsys.readouterr()
    assert "[Success] Item added successfully!" in captured.out


""" Tests the update_item function"""
@patch('cli.requests.patch')
@patch('builtins.input', side_effect=['1', 'price', '3.50'])
def test_update_item_price_success(mock_input, mock_patch, capsys: CaptureFixture[str]):
    mock_patch.return_value = mock_response(200)

    update_item()

    mock_patch.assert_called_once_with(
        f"{BASE_URL}/inventory/1",
        json={"price": 3.5}
    )
    captured = capsys.readouterr()
    assert "Item updated successfully!" in captured.out


""" Tests for delete_item function """
@patch('cli.requests.delete')
@patch('builtins.input', return_value='1')
def test_delete_item_success(mock_input, mock_delete, capsys: CaptureFixture[str]):
    mock_delete.return_value = mock_response(200)

    delete_item()

    mock_delete.assert_called_once_with(f"{BASE_URL}/inventory/1")
    captured = capsys.readouterr()
    assert "Item 1 deleted successfully!" in captured.out


""" This function tests the external API call to OpenFoodFacts"""
@patch('cli.fetch_external_data')
@patch('builtins.input', side_effect=['1', '123456789'])
def test_find_on_api_barcode_success(mock_input, mock_fetch, capsys: CaptureFixture[str]):
    # Mock the imported function directly
    mock_fetch.return_value = {
        "name": "Test Drink",
        "brand": "TestCo",
        "category": "Beverages"
    }

    find_on_api()

    mock_fetch.assert_called_once_with('123456789', 'barcode')
    captured = capsys.readouterr()
    assert "Name: Test Drink" in captured.out
    assert "Brand: TestCo" in captured.out