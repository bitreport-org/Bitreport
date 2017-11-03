class BtcWallet
  def self.derive(id)
    master = MoneyTree::Node.from_bip32 Settings.bitcoin.master_public_key
    node = master.node_for_path Settings.bitcoin.node_path + id.to_s

    node.to_address(network: Settings.bitcoin.network.to_sym)
  end
end
