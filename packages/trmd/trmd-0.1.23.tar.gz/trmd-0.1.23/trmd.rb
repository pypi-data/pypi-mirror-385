class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/5e/b0/bdde4109b514901804149a7030bf9635a7208de62f8f25d4bb8ac363f7ae/trmd-0.1.22.tar.gz"
  sha256 "cc3ae238de61c16b868169ce7cecff6d58df139d07394ce25c59cfe0f87fdaa6"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
