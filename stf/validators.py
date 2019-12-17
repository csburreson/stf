import abc
import numbers
import re
from future.utils import with_metaclass
import openhtf as htf
import six
import stf

class EqualsParam(htf.util.validators.ValidatorBase):
    def __init__(self, pvalue, type=None):
        self.paramValue = pvalue
        self._type = type

    def __call__(self, value):
        if self._type:
            return self._type(self.paramValue) == value
        return self.paramValue == value
        
    def __str__(self):
        '''use in output'''
        return 'x == {}'.format(self.paramValue)

    def with_args(self, **kw):
        try:
            return type(self)(
                pvalue=htf.util.format_string(self.paramValue, self.expectedValues),
                type=self._type
            )
        except KeyError:
            raise Exception('Framework Error. Contact maintainer')

@htf.util.validators.register
def equalsParam(pname, type=None):
    stf.debug('use "expect" instead of equalsParam')
    if not (pname.startswith('{') and pname.endswith('}')):
        pname = '{' + pname + '}'
    return EqualsParam(pname, type=type)

@htf.util.validators.register
def expect(pname, type=None):
    if not (pname.startswith('{') and pname.endswith('}')):
        pname = '{' + pname + '}'
    stf.debug('type: {}'.format(type))
    return EqualsParam(pname, type=type)



# Built-in validators below this line

class InRange(htf.util.validators.RangeValidatorBase):
  """Validator to verify a numeric value is within a range."""

  def __init__(self, minimum=None, maximum=None, type=None):
    if minimum is None and maximum is None:
      raise ValueError('Must specify minimum, maximum, or both')
    if (minimum is not None and maximum is not None
        and isinstance(minimum, numbers.Number)
        and isinstance(maximum, numbers.Number)
        and minimum > maximum):
      raise ValueError('Minimum cannot be greater than maximum')
    self._minimum = minimum
    self._maximum = maximum
    self._type = type

  @property
  def minimum(self):
    converter = self._type if self._type is not None else _identity
    return converter(self._minimum)

  @property
  def maximum(self):
    converter = self._type if self._type is not None else _identity
    return converter(self._maximum)

  def with_args(self, **kwargs):
    return type(self)(
        minimum=htf.util.format_string(self._minimum, self.expectedValues),
        maximum=htf.util.format_string(self._maximum, self.expectedValues),
        type=self._type,
    )

  def __call__(self, value):
    if value is None:
      return False
    import math
    # Check for nan (but allow strings)
    if not isinstance(value, six.string_types) and math.isnan(value):
      return False
    if self.minimum is not None and value < self.minimum:
      return False
    if self.maximum is not None and value > self.maximum:
      return False
    return True

  def __str__(self):
    assert self._minimum is not None or self._maximum is not None
    if self._minimum is not None and self._maximum is not None:
      if self._minimum == self._maximum:
        return 'x == %s' % self._minimum
      return '%s <= x <= %s' % (self._minimum, self._maximum)
    if self._minimum is not None:
      return '%s <= x' % self._minimum
    if self._maximum is not None:
      return 'x <= %s' % self._maximum

  def __eq__(self, other):
    return (isinstance(other, type(self)) and
            self.minimum == other.minimum and self.maximum == other.maximum)

  def __ne__(self, other):
    return not self == other

in_range = InRange  # pylint: disable=invalid-name
htf.util.validators.register(InRange, name='expectRange')


class RegexMatcher(htf.util.validators.ValidatorBase):
  """Validator to verify a string value matches a regex."""

  def __init__(self, regex, compiled_regex):
    self._compiled = re.compile(regex)
   # compiled_regex
    self.regex = regex

  def __call__(self, value):
    #value = htf.util.format_string(value, self.expectedValues) 
    return self._compiled.match(str(value)) is not None
  
  def with_args(self, **kw):
    r = htf.util.format_string(self.regex, self.expectedValues)
    self.regex = r
    self._compiled = re.compile(r)
    return type(self)(self.regex, self._compiled)

  def __deepcopy__(self, dummy_memo):
    return type(self)(self.regex, self._compiled)

  def __str__(self):
    return "'x' matches /%s/" % self.regex

  def __eq__(self, other):
    return isinstance(other, type(self)) and self.regex == other.regex

  def __ne__(self, other):
    return not self == other


@htf.util.validators.register
def expectRegex(regex):
  return RegexMatcher(regex, re.compile(regex))


class WithinPercent(htf.util.validators.RangeValidatorBase):
  """Validates that a number is within percent of a value."""

  def __init__(self, expected, percent):
    #if percent < 0:
    #  raise ValueError('percent argument is {}, must be >0'.format(percent))
    self.expected = expected
    self.percent = percent

  @property
  def _applied_percent(self):
    return abs(self.expected * self.percent / 100.0)

  @property
  def minimum(self):
    return self.expected - self._applied_percent

  @property
  def maximum(self):
    return self.expected + self._applied_percent

  def __call__(self, value):
    #value = float(htf.util.format_string(value, self.expectedValue))
    return self.minimum <= value <= self.maximum

  def __str__(self):
    return "'x' is within {}% of {}".format(self.percent, self.expected)

  def __eq__(self, other):
    return (isinstance(other, type(self)) and
            self.expected == other.expected and
            self.percent == other.percent)

  def __ne__(self, other):
    return not self == other

  def with_args(self, **kw):
    return type(self)(
        float(htf.util.format_string(self.expected, self.expectedValues)),
        float(htf.util.format_string(self.percent, self.expectedValues)),
    )

@htf.util.validators.register
def expectPercent(expected, percent):
  return WithinPercent(expected, percent)



