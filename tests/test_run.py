import unittest


class DoesItRun(unittest.TestCase):
    def testClone(self):
        from pyauric import AURICManager
        # This is the default manager
        auric = AURICManager()
        self.assertIsNotNone(auric)

        # Create a clone in a temporary directory.
        # Test that it is in fact an AURICManager and that the key
        # input files exist.
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix="pyauric-test-") as tempdir:
            tempauric = auric.clone(tempdir)
            self.assertIsInstance(tempauric, AURICManager)
            from os import path
            self.assertEqual(tempauric.pathto("dbpath.inp"), path.join(tempdir, "dbpath.inp"))
            self.assertTrue(path.exists(tempauric.pathto("dbpath.inp")))
            self.assertTrue(path.exists(tempauric.pathto("param.inp")))
            self.assertTrue(path.exists(tempauric.pathto("view.inp")))


if __name__ == "__main__":
    unittest.main()
