from PyObjCTools.TestSupport import TestCase
import Vision


class TestVNError(TestCase):
    def test_enum_types(self):
        self.assertIsEnumType(Vision.VNErrorCode)

    def testConstants(self):
        self.assertEqual(Vision.VNErrorOK, 0)
        self.assertEqual(Vision.VNErrorRequestCancelled, 1)
        self.assertEqual(Vision.VNErrorInvalidFormat, 2)
        self.assertEqual(Vision.VNErrorOperationFailed, 3)
        self.assertEqual(Vision.VNErrorOutOfBoundsError, 4)
        self.assertEqual(Vision.VNErrorInvalidOption, 5)
        self.assertEqual(Vision.VNErrorIOError, 6)
        self.assertEqual(Vision.VNErrorMissingOption, 7)
        self.assertEqual(Vision.VNErrorNotImplemented, 8)
        self.assertEqual(Vision.VNErrorInternalError, 9)
        self.assertEqual(Vision.VNErrorOutOfMemory, 10)
        self.assertEqual(Vision.VNErrorUnknownError, 11)
        self.assertEqual(Vision.VNErrorInvalidOperation, 12)
        self.assertEqual(Vision.VNErrorInvalidImage, 13)
        self.assertEqual(Vision.VNErrorInvalidArgument, 14)
        self.assertEqual(Vision.VNErrorInvalidModel, 15)
        self.assertEqual(Vision.VNErrorUnsupportedRevision, 16)
        self.assertEqual(Vision.VNErrorDataUnavailable, 17)
        self.assertEqual(Vision.VNErrorTimeStampNotFound, 18)
        self.assertEqual(Vision.VNErrorUnsupportedRequest, 19)
        self.assertEqual(Vision.VNErrorTimeout, 20)
        self.assertEqual(Vision.VNErrorUnsupportedComputeStage, 21)
        self.assertEqual(Vision.VNErrorUnsupportedComputeDevice, 22)
