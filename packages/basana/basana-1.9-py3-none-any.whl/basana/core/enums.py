# Basana
#
# Copyright 2022 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum


# Using these values to avoid misunderstandings with external API values.
@enum.unique
class OrderOperation(enum.Enum):
    """Enumeration for order operations."""

    #:
    BUY = 100
    #:
    SELL = 101

    def __str__(self):
        return {
            OrderOperation.BUY: "buy",
            OrderOperation.SELL: "sell",
        }[self]


@enum.unique
class Position(enum.Enum):
    """Enumeration for positions."""

    #:
    LONG = 200
    #:
    SHORT = 201
    #:
    NEUTRAL = 202

    def __str__(self):
        return {
            Position.LONG: "long",
            Position.SHORT: "short",
            Position.NEUTRAL: "neutral",
        }[self]
