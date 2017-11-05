class BtcWallet
  include MoneyTree::Support

  OP_2 = 0x52.to_s(16).freeze
  OP_CHECKMULTISIG = 0xAE.to_s(16).freeze

  attr_reader :id

  def initialize(id)
    @id = id
  end

  def derive
    @script ||= script
  end

  private

  def script
    script = '' << OP_2
    derived_addresses(id).each do |addr|
      script << bytes(addr) << addr
    end
    script << OP_2 << OP_CHECKMULTISIG

    serialize(script)
  end

  def bytes(str)
    [str].pack('H*').size.to_s(16)
  end

  def derived_addresses(id)
    Settings.bitcoin.master_public_keys.map do |key|
      master = MoneyTree::Node.from_bip32(key)
      node = master.node_for_path(Settings.bitcoin.node_path + id.to_s)
      node.public_key.key
    end.sort
  end

  def prefix
    MoneyTree::NETWORKS[Settings.bitcoin.network.to_sym][:p2sh_version]
  end

  def serialize(str)
    to_serialized_base58(prefix + ripemd160(sha256(str)))
  end
end
