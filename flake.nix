{
  inputs.nixpkgs.url  = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs:
  let
    flake = inputs: system: nixpkgs.lib.mapAttrs (name: flake: {
      # TODO filter non-flake inputs
      nixos = flake.nixosModules
        or null;
      pkgs = flake.packages.${system}
        or flake.legacyPackages.${system}
        or null;
      lib = flake.lib.${system}
        or flake.lib
        or null;
    }) inputs;
    forSystems = systems: f: nixpkgs.lib.genAttrs systems (system: f rec {
      inherit system;
      pkgs = nixpkgs.legacyPackages.${system};
      lib  = nixpkgs.legacyPackages.${system}.lib;
      flakes = flake inputs system;
    });
    forAllSystems = forSystems [
      "x86_64-linux"
      "aarch64-linux"
      #"riscv64-linux"
    ];
  in {
    inherit inputs;

    packages = forAllSystems ({ pkgs, flakes, ...}: {
      remi = with pkgs.python3.pkgs; buildPythonPackage rec {
        pname = "remi";
        version = "1.0";
        src = fetchPypi {
          inherit pname version;
          hash = "sha256-65qc+td/mk/RSUcRWbPGVbS9S0F1o1S9zIkJb0Ek2eQ=";
          extension = "zip";
        };
        pyproject = true;
        build-system = [ setuptools ];
        dependencies = [ legacy-cgi ];
        # https://github.com/rawpython/remi/issues/216
        postPatch = ''
          substituteInPlace remi/server.py \
            --replace \
              "WebSocket('ws://%s:%s/');" \
              "WebSocket('wss://%s/websocket'); // %s"
        '';
      };
      grzegorz-clients = with pkgs.python3.pkgs; buildPythonPackage {
        pname = "grzegorz-clients";
        version = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).tool.poetry.version;
        pyproject = true;
        src = ./.;
        nativeBuildInputs = [ poetry-core ];
        propagatedBuildInputs = [ setuptools flakes.self.pkgs.remi requests typer rich urllib3 ];
      };
      grzegorzctl = pkgs.runCommandNoCCLocal "grzegorzctl" (
        {
          nativeBuildInputs = [ pkgs.installShellFiles ];
        } //
        { inherit (flakes.self.pkgs.grzegorz-clients) meta; } //
        { meta.mainProgram = "grzegorzctl"; }
      )''
        mkdir -p $out/bin
        ln -s "${flakes.self.pkgs.grzegorz-clients}/bin/grzegorzctl" $out/bin/grzegorzctl
        installShellCompletion --cmd grzegorzctl \
          --bash <($out/bin/grzegorzctl --show-completion bash) \
          --zsh <($out/bin/grzegorzctl --show-completion zsh) \
          --fish <($out/bin/grzegorzctl --show-completion fish)
      '';
      default = flakes.self.pkgs.grzegorzctl;
    });

    checks = forAllSystems ({ system, ... }: {
      inherit (self.packages.${system}) grzegorzctl grzegorz-clients;
    });

    apps = forAllSystems ({ system, ...}: rec {
      grzegorz-webui.type = "app";
      grzegorz-webui.program = "${self.packages.${system}.grzegorz-clients}/bin/grzegorz-webui";
      grzegorzctl.type = "app";
      grzegorzctl.program = "${self.packages.${system}.grzegorzctl}/bin/grzegorzctl";
      default = grzegorzctl;
    });

    nixosModules.grzegorz-webui = { config, pkgs, ... }: let
      inherit (pkgs) lib;
      cfg = config.services.grzegorz-webui;
    in {
      options.services.grzegorz-webui = {

        enable = lib.mkEnableOption (lib.mdDoc "grzegorz");

        package = lib.mkPackageOption self.packages.${config.nixpkgs.system} "grzegorz-clients" { };

        listenAddr = lib.mkOption {
          type = lib.types.str;
          default = "::";
        };
        listenPort = lib.mkOption {
          type = lib.types.port;
          default = 8080;
        };
        listenWebsocketPort = lib.mkOption {
            type = lib.types.port;
            default = 0;
        };
        multipleInstance = lib.mkOption {
          type = lib.types.bool;
          default = false;
        };
        hostName = lib.mkOption {
          type = lib.types.str;
          default = "brzeczyszczykiewicz.pvv.ntnu.no";
        };
        apiBase = lib.mkOption {
          type = lib.types.str;
          default = "https://brzeczyszczykiewicz.pvv.ntnu.no/api";
        };
      };
      config = {
        systemd.services.grzegorz-webui = lib.mkIf cfg.enable {
          description = "grzegorz-webui";
          after = [ "network.target" ];
          wantedBy = [ "multi-user.target" ];
          serviceConfig = {
            User = "grzegorz-webui";
            Group = "grzegorz-webui";
            DynamicUser = true;
            #StateDirectory = "grzegorz-webui";
            #CacheDirectory = "grzegorz-webui";
            ExecStart = lib.escapeShellArgs [
              "${cfg.package}/bin/grzegorz-webui"
              "--address" cfg.listenAddr
              "--port" cfg.listenPort
              "--host-name" cfg.hostName
              "--api-base" cfg.apiBase
              "--websocket-port" cfg.listenWebsocketPort
              (if cfg.multipleInstance
                then "--multiple-instance"
                else "--no-multiple-instance")
            ];
            Restart = "on-failure";
          };
        };
      };
    };

    devShells = forAllSystems ({ pkgs, ... }: rec {
      default = pkgs.mkShellNoCC {
        packages = [
          pkgs.poetry
          pkgs.python3
          pkgs.entr
        ];
      };
    });
  };
}
