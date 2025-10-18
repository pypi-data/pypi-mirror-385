from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.free_text import data_free_text
from mai_bias.catalogue.model_loaders.no_model import no_model
from mai_bias.catalogue.metrics.text_dbias import text_debias


def test_bias_exploration():
    with testing.Env(data_free_text, no_model, text_debias) as env:
        text = "The non-existent Rufus of the Fifth Sky in the fantasy dreamland is opposed to the anti-black movement."
        markdown_result = env.text_debias(env.data_free_text(text), env.no_model(), [])
        markdown_result.show()


if __name__ == "__main__":
    test_bias_exploration()
