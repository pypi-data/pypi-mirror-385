import torch
import unittest

from torchness.initialize import my_initializer


class TestInitialize(unittest.TestCase):

    def test_my_initializer(self):
        tns = torch.zeros(1000)
        #print(tns)
        my_initializer(tns, std=0.1)
        #print(tns)
        print(tns.numpy().std())
        self.assertTrue(0.08 < tns.numpy().std() < 0.12)

