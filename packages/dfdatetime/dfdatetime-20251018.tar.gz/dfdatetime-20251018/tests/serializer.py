#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the date and time values serializer."""

import unittest

from dfdatetime import dotnet_datetime
from dfdatetime import fat_date_time
from dfdatetime import golang_time
from dfdatetime import posix_time
from dfdatetime import rfc2579_date_time
from dfdatetime import semantic_time
from dfdatetime import serializer
from dfdatetime import systemtime
from dfdatetime import time_elements


class SerializerTest(unittest.TestCase):
  """Tests for the date and time values serializer."""

  def testConvertDateTimeValuesToJSON(self):
    """Test ConvertDateTimeValuesToJSON function."""
    posix_time_object = posix_time.PosixTime(timestamp=1281643591)

    expected_json_dict = {
        '__class_name__': 'PosixTime',
        '__type__': 'DateTimeValues',
        'timestamp': 1281643591}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        posix_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    posix_time_object.is_local_time = True
    posix_time_object.time_zone_hint = 'Europe/Amsterdam'

    expected_json_dict = {
        '__class_name__': 'PosixTime',
        '__type__': 'DateTimeValues',
        'is_local_time': True,
        'time_zone_hint': 'Europe/Amsterdam',
        'timestamp': 1281643591}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        posix_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    posix_time_object = posix_time.PosixTime(
        timestamp=1281643591, time_zone_offset=60)

    expected_json_dict = {
        '__class_name__': 'PosixTime',
        '__type__': 'DateTimeValues',
        'timestamp': 1281643591,
        'time_zone_offset': 60}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        posix_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    never_time_object = semantic_time.Never()

    expected_json_dict = {
        '__class_name__': 'Never',
        '__type__': 'DateTimeValues',
        'string': 'Never'}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        never_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    dotnet_datetime_object = dotnet_datetime.DotNetDateTime(
        timestamp=637433719321230000)

    expected_json_dict = {
        '__class_name__': 'DotNetDateTime',
        '__type__': 'DateTimeValues',
        'timestamp': 637433719321230000}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        dotnet_datetime_object)
    self.assertEqual(json_dict, expected_json_dict)

    fat_date_time_object = fat_date_time.FATDateTime(fat_date_time=0xa8d03d0c)

    expected_json_dict = {
        '__class_name__': 'FATDateTime',
        '__type__': 'DateTimeValues',
        'fat_date_time': 2832219404}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        fat_date_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    golang_timestamp = bytes.fromhex('01000000000000000200000003ffff')
    golang_time_object = golang_time.GolangTime(
        golang_timestamp=golang_timestamp)

    expected_json_dict = {
        '__class_name__': 'GolangTime',
        '__type__': 'DateTimeValues',
        'golang_timestamp': (
            b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x03\xff\xff')}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        golang_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    rfc2579_date_time_object = rfc2579_date_time.RFC2579DateTime(
        rfc2579_date_time_tuple=(2010, 8, 12, 20, 6, 31, 6, '+', 2, 0))

    expected_json_dict = {
        '__class_name__': 'RFC2579DateTime',
        '__type__': 'DateTimeValues',
        'rfc2579_date_time_tuple': (2010, 8, 12, 20, 6, 31, 6, '+', 2, 0)}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        rfc2579_date_time_object)
    self.assertEqual(json_dict, expected_json_dict)

    systemtime_object = systemtime.Systemtime(
        system_time_tuple=(2010, 8, 4, 12, 20, 6, 31, 142))

    expected_json_dict = {
        '__class_name__': 'Systemtime',
        '__type__': 'DateTimeValues',
        'system_time_tuple': (2010, 8, 4, 12, 20, 6, 31, 142)}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        systemtime_object)
    self.assertEqual(json_dict, expected_json_dict)

    time_elements_object = time_elements.TimeElements(
        is_delta=True, time_elements_tuple=(2010, 8, 12, 20, 6, 31))

    expected_json_dict = {
        '__class_name__': 'TimeElements',
        '__type__': 'DateTimeValues',
        'is_delta': True,
        'time_elements_tuple': (2010, 8, 12, 20, 6, 31)}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        time_elements_object)
    self.assertEqual(json_dict, expected_json_dict)

    time_elements_object = time_elements.TimeElementsInMilliseconds(
        time_elements_tuple=(2010, 8, 12, 20, 6, 31, 546))

    expected_json_dict = {
        '__class_name__': 'TimeElementsInMilliseconds',
        '__type__': 'DateTimeValues',
        'time_elements_tuple': (2010, 8, 12, 20, 6, 31, 546)}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        time_elements_object)
    self.assertEqual(json_dict, expected_json_dict)

    time_elements_object = time_elements.TimeElementsInMicroseconds(
        time_elements_tuple=(2010, 8, 12, 20, 6, 31, 429876))

    expected_json_dict = {
        '__class_name__': 'TimeElementsInMicroseconds',
        '__type__': 'DateTimeValues',
        'time_elements_tuple': (2010, 8, 12, 20, 6, 31, 429876)}

    json_dict = serializer.Serializer.ConvertDateTimeValuesToJSON(
        time_elements_object)
    self.assertEqual(json_dict, expected_json_dict)

  def testConvertJSONToDateTimeValues(self):
    """Test ConvertJSONToDateTimeValues function."""
    json_dict = {
        '__class_name__': 'PosixTime',
        '__type__': 'DateTimeValues',
        'timestamp': 1281643591}

    expected_date_time_object = posix_time.PosixTime(timestamp=1281643591)

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'PosixTime',
        '__type__': 'DateTimeValues',
        'is_local_time': True,
        'time_zone_hint': 'Europe/Amsterdam',
        'timestamp': 1281643591}

    expected_date_time_object.is_local_time = True
    expected_date_time_object.time_zone_hint = 'Europe/Amsterdam'

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'PosixTime',
        '__type__': 'DateTimeValues',
        'timestamp': 1281643591,
        'time_zone_offset': 60}

    expected_date_time_object = posix_time.PosixTime(
        timestamp=1281643591, time_zone_offset=60)

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'Never',
        '__type__': 'DateTimeValues',
        'string': 'Never'}

    expected_date_time_object = semantic_time.Never()

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'DotNetDateTime',
        '__type__': 'DateTimeValues',
        'timestamp': 637433719321230000}

    expected_date_time_object = dotnet_datetime.DotNetDateTime(
        timestamp=637433719321230000)

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'FATDateTime',
        '__type__': 'DateTimeValues',
        'fat_date_time': 2832219404}

    expected_date_time_object = fat_date_time.FATDateTime(
        fat_date_time=0xa8d03d0c)

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'GolangTime',
        '__type__': 'DateTimeValues',
        'golang_timestamp': (
            b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x03\xff\xff')}

    golang_timestamp = bytes.fromhex('01000000000000000200000003ffff')
    expected_date_time_object = golang_time.GolangTime(
        golang_timestamp=golang_timestamp)

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'RFC2579DateTime',
        '__type__': 'DateTimeValues',
        'rfc2579_date_time_tuple': (2010, 8, 12, 20, 6, 31, 6, '+', 2, 0)}

    expected_date_time_object = rfc2579_date_time.RFC2579DateTime(
        rfc2579_date_time_tuple=(2010, 8, 12, 20, 6, 31, 6, '+', 2, 0))

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'Systemtime',
        '__type__': 'DateTimeValues',
        'system_time_tuple': (2010, 8, 4, 12, 20, 6, 31, 142)}

    expected_date_time_object = systemtime.Systemtime(
        system_time_tuple=(2010, 8, 4, 12, 20, 6, 31, 142))

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'TimeElements',
        '__type__': 'DateTimeValues',
        'is_delta': True,
        'time_elements_tuple': (2010, 8, 12, 20, 6, 31)}

    expected_date_time_object = time_elements.TimeElements(
        is_delta=True, time_elements_tuple=(2010, 8, 12, 20, 6, 31))

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)
    self.assertTrue(date_time_object.is_delta)

    json_dict = {
        '__class_name__': 'TimeElementsInMilliseconds',
        '__type__': 'DateTimeValues',
        'time_elements_tuple': (2010, 8, 12, 20, 6, 31, 546)}

    expected_date_time_object = time_elements.TimeElementsInMilliseconds(
        time_elements_tuple=(2010, 8, 12, 20, 6, 31, 546))

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)

    json_dict = {
        '__class_name__': 'TimeElementsInMicroseconds',
        '__type__': 'DateTimeValues',
        'time_elements_tuple': (2010, 8, 12, 20, 6, 31, 429876)}

    expected_date_time_object = time_elements.TimeElementsInMicroseconds(
        time_elements_tuple=(2010, 8, 12, 20, 6, 31, 429876))

    date_time_object = serializer.Serializer.ConvertJSONToDateTimeValues(
        json_dict)
    self.assertEqual(date_time_object, expected_date_time_object)


if __name__ == '__main__':
  unittest.main()
