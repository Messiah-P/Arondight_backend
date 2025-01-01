from controller.common.adapter import Adapter


class PixivInputAdapter(Adapter):

    @staticmethod
    def encoder(response):
        pass

    @staticmethod
    def decoder(request):
        txn_code = request.txn_code
        txn_subcode = request.txn_subcode
        return txn_code, txn_subcode
