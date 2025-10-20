from PrismSSL.audio.models.modules.losses.hubert_loss import HuBERTLoss
from PrismSSL.audio.models.modules.losses.wav2vec2_loss import Wav2Vec2Loss
from PrismSSL.audio.models.modules.losses.infoNCE_loss import InfoNCELoss
from PrismSSL.audio.models.modules.losses.ufo_loss import UFO


__all__ = ["HuBERTLoss", "Wav2Vec2Loss", "InfoNCELoss", "UFO"]