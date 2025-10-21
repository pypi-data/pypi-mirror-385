from copy import deepcopy
from decimal import Decimal

from pydantic import ValidationError
from pytest import raises

from .common import check_error
from .data import test_wage

from usdol_wage_determination_model import Holiday, Wage


def test_basic_values():
    wage = Wage(**test_wage)
    assert wage.currency == test_wage['currency']
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe.fixed == Decimal(test_wage['fringe']['fixed'])
    assert wage.fringe.percentage == Decimal(test_wage['fringe']['percentage'])


def test_zero_values():
    test_zero_values = deepcopy(test_wage)
    test_zero_values['rate'] = '0.0'
    test_zero_values['fringe'] = {'fixed': '0.0', 'percentage': '0.0'}
    wage = Wage(**test_zero_values)
    assert wage.currency == test_wage['currency']
    assert wage.rate == Decimal('0.0')
    assert wage.fringe.fixed == Decimal('0.0')
    assert wage.fringe.percentage == Decimal('0.0')


def test_default_currency():
    test_default_currency = deepcopy(test_wage)
    del test_default_currency['currency']
    wage = Wage(**test_default_currency)
    assert wage.currency == test_wage['currency']
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe.fixed == Decimal(test_wage['fringe']['fixed'])
    assert wage.fringe.percentage == Decimal(test_wage['fringe']['percentage'])


def test_alternate_currency():
    test_alt_currency = deepcopy(test_wage)
    test_alt_currency['currency'] = 'EUR'
    wage = Wage(**test_alt_currency)
    assert wage.currency == 'EUR'
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe.fixed == Decimal(test_wage['fringe']['fixed'])
    assert wage.fringe.percentage == Decimal(test_wage['fringe']['percentage'])


def test_fringe_fixed_only():
    test_fringe_fixed_only = deepcopy(test_wage)
    del test_fringe_fixed_only['fringe']['percentage']
    wage = Wage(**test_fringe_fixed_only)
    assert wage.currency == 'USD'
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe.fixed == Decimal(test_wage['fringe']['fixed'])
    assert wage.fringe.percentage is None


def test_fringe_percentage_only():
    test_fringe_percentage_only = deepcopy(test_wage)
    del test_fringe_percentage_only['fringe']['fixed']
    wage = Wage(**test_fringe_percentage_only)
    assert wage.currency == 'USD'
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe.fixed is None
    assert wage.fringe.percentage == Decimal(test_wage['fringe']['percentage'])


def test_fractional_values():
    test_fractional_values = deepcopy(test_wage)
    test_fractional_values['rate'] = '123.456'
    test_fractional_values['fringe']['fixed'] = '12.345'
    wage = Wage(**test_fractional_values)
    assert wage.currency == 'USD'
    assert wage.rate == Decimal('123.456')
    assert wage.fringe.fixed == Decimal('12.345')
    assert wage.fringe.percentage == Decimal(test_wage['fringe']['percentage'])


def test_holidays():
    all_holidays = {h.value for h in Holiday}
    test_holidays = deepcopy(test_wage)
    test_holidays['fringe']['holidays'] = all_holidays
    wage = Wage(**test_holidays)
    assert wage.fringe.holidays == all_holidays


def test_bad_currency():
    test_bad_currency = deepcopy(test_wage)
    test_bad_currency['currency'] = 'FOO'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Invalid currency code.')


def test_bad_rate():
    test_bad_rate = deepcopy(test_wage)
    del test_bad_rate['rate']
    with raises(ValidationError) as error:
        Wage(**test_bad_rate)
    check_error(error, 'Field required')
    test_bad_rate['rate'] = None
    with raises(ValidationError) as error:
        Wage(**test_bad_rate)
    check_error(error, 'Decimal input should be an integer, float, string or Decimal object')
    test_bad_rate['rate'] = 'foo'
    with raises(ValidationError) as error:
        Wage(**test_bad_rate)
    check_error(error, 'Input should be a valid decimal')
    test_bad_rate['rate'] = '-123.45'
    with raises(ValidationError) as error:
        Wage(**test_bad_rate)
    check_error(error, 'Input should be greater than or equal to 0.0')
    test_bad_rate['rate'] = '12.3456'
    with raises(ValidationError) as error:
        Wage(**test_bad_rate)
    check_error(error, 'Decimal input should have no more than 3 decimal places')
    test_bad_rate['rate'] = '1234.567'
    with raises(ValidationError) as error:
        Wage(**test_bad_rate)
    check_error(error, 'Decimal input should have no more than 6 digits in total')


def test_bad_fringe():
    test_bad_fringe = deepcopy(test_wage)
    test_bad_fringe['fringe'] = None
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be a valid dictionary or instance of Fringe')
    test_bad_fringe['fringe'] = 'foo'
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be a valid dictionary or instance of Fringe')
    test_bad_fringe['fringe'] = '12.34'
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be a valid dictionary or instance of Fringe')
    test_bad_fringe['fringe'] = {'fixed': None}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should be an integer, float, string or Decimal object')
    test_bad_fringe['fringe'] = {}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Value error, At least one of fixed or percentage must be provided')
    test_bad_fringe['fringe'] = {'fixed': 'foo'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be a valid decimal')
    test_bad_fringe['fringe'] = {'fixed': '-123.45'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be greater than or equal to 0.0')
    test_bad_fringe['fringe'] = {'fixed': '12.3456'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should have no more than 3 decimal places')
    test_bad_fringe['fringe'] = {'fixed': '1234.567'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should have no more than 6 digits in total')
    test_bad_fringe['fringe'] = {'percentage': None}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should be an integer, float, string or Decimal object')
    test_bad_fringe['fringe'] = {'percentage': 'foo'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be a valid decimal')
    test_bad_fringe['fringe'] = {'percentage': '-0.123'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Input should be greater than or equal to 0.0')
    test_bad_fringe['fringe'] = {'percentage': '0.1234'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should have no more than 3 decimal places')
    test_bad_fringe['fringe'] = {'percentage': '1.2345'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should have no more than 4 digits in total')
    test_bad_fringe['fringe'] = {'percentage': '12.234'}
    with raises(ValidationError) as error:
        Wage(**test_bad_fringe)
    check_error(error, 'Decimal input should have no more than 4 digits in total')


def test_bad_holidays():
    test_bad_holidays = deepcopy(test_wage)
    test_bad_holidays['fringe']['holidays'] = None
    with raises(ValidationError) as error:
        Wage(**test_bad_holidays)
    check_error(error, 'Input should be a valid set')
    test_bad_holidays['fringe']['holidays'] = 'Not A Holiday'
    with raises(ValidationError) as error:
        Wage(**test_bad_holidays)
    check_error(error, 'Input should be a valid set')
    test_bad_holidays['fringe']['holidays'] = {'Not A Holiday'}
    with raises(ValidationError) as error:
        Wage(**test_bad_holidays)
    check_error(error, 'Input should be "New Year\'s Day"')
