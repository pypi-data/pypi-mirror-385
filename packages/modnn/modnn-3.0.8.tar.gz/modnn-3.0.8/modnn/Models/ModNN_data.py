import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# --- Zone Module ---
class zone(nn.Module):
    """
    Assume well-mixed condition, and we have: Q = cmΔTzone
    In other words, ΔTzone = Q/cm, that can be learned by a simple linear layer
    The input of this module is ∑q, each q is calculated by distinct module shown below
    """
    def __init__(self, input_size, output_size):
        super(zone, self).__init__()
        # Set bias to False here is important, since this module is learning a weight only (cm)
        self.scale = nn.Linear(input_size, output_size, bias=False)

    def forward(self, x):
        return self.scale(x)

# --- Zone Module ---
# class zone(nn.Module):
#     def __init__(self, input_size, hidden_size, output_size, num_layers=1):
#         super(zone, self).__init__()
#         self.dym = nn.RNN(input_size=input_size, hidden_size=hidden_size,
#                                           num_layers=num_layers, batch_first=True, bias=True)
#         self.fc = nn.Linear(hidden_size, output_size)
#
#     def forward(self, deltaq, hidden):
#         Tpred, hidden = self.dym(deltaq, hidden)
#         out = self.fc(Tpred)
#
#         return out, hidden

# --- Internal Gain Module ---
class internal(nn.Module):
    """
    The internal heat gain module we used here is a simple MLP
    We use it to calculate the q_int from convection ONLY
    There are two ways to consider the internal heat gain from radiation heat transfer
    1) Replace MLP by any type of RNN
    2) Add a lookback window for MLP (for example, use t-N to t steps feature to predict the t step's heat gain)

    The internal heat gain comes from Lighting, Occupant, Appliance, so on so forth
    But they can be represented by a factor (alpha) multiply with a "schedule" (sch), for example:
    q_light = alpha_light * sch_light
    q_human = alpha_human * sch_human
    q_cooking = alpha_cooking * sch_cooking

    If detailed information is available, we can replace it by Physics Equations
    For example, 80~100W * Number_of_people
    Otherwise, we learn form periodic features, such as time of a day, day of a week, in sin/cos form
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(internal, self).__init__()
        self.FC1 = nn.Linear(input_size-1, hidden_size)
        self.FC2 = nn.Linear(hidden_size, output_size)
        self.scale = nn.Linear(1, 1, bias=False)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        embedding = self.FC1(x[:, :, :-1])
        embedding = self.relu(embedding)
        embedding = self.FC2(embedding)
        # embedding = self.sigmoid(embedding) #Force output to 0--1
        embedding = embedding + x[:, :, -1:]
        return self.scale(embedding)

# --- HVAC Module ---
class hvac(nn.Module):
    """
    A simplified linear module is used here for AIR SIDE SYSTEM ONLY
    Change it to any type of RNN or add look back window for RADIATION SYSTEM

    The input is pre-calculated pHVAC (thermal load)
    But if the raw data is HVAC energy, or supply air flow/temperature
    No worry, we can add another system module to learn this relation easy
    """
    def __init__(self, input_size, output_size):
        super(hvac, self).__init__()
        self.scale = nn.Linear(input_size, output_size, bias=False)

    def forward(self, x):
        return self.scale(x)


class PhysicsInformedEnvelope(nn.Module):
    """
    Physics-informed envelope module using convolutional response factors.
    This module mimics EnergyPlus's response factor approach while being learnable.
    """

    def __init__(self, n_surfaces=1, response_length=24, hidden_dim=16,
                 enforce_strict_physics=True, allow_oscillation=False):
        super(PhysicsInformedEnvelope, self).__init__()

        # Response factor kernels (learnable)
        # These act like discrete Green's functions for the PDE
        self.response_length = response_length
        self.enforce_strict_physics = enforce_strict_physics
        self.allow_oscillation = allow_oscillation

        if allow_oscillation:
            # For materials with complex thermal behavior (e.g., phase change materials)
            # Allow response factors to have oscillatory components
            # Use Prony series representation: sum of exponentially decaying sinusoids
            self.n_modes = 3  # Number of Prony modes

            # Parameters for each mode: amplitude, decay rate, frequency
            self.ext_amplitudes = nn.Parameter(torch.randn(n_surfaces, self.n_modes, 1) * 0.1)
            self.ext_decay_rates = nn.Parameter(torch.ones(n_surfaces, self.n_modes, 1) * 0.5)
            self.ext_frequencies = nn.Parameter(torch.randn(n_surfaces, self.n_modes, 1) * 0.1)

            self.int_amplitudes = nn.Parameter(torch.randn(n_surfaces, self.n_modes, 1) * 0.1)
            self.int_decay_rates = nn.Parameter(torch.ones(n_surfaces, self.n_modes, 1) * 0.5)
            self.int_frequencies = nn.Parameter(torch.randn(n_surfaces, self.n_modes, 1) * 0.1)
        else:
            # Standard monotonic decay response factors
            # External response factors (how external temp affects heat flux)
            self.ext_response = nn.Parameter(torch.randn(n_surfaces, 1, response_length) * 0.1)

            # Internal response factors (how internal temp affects heat flux)
            self.int_response = nn.Parameter(torch.randn(n_surfaces, 1, response_length) * 0.1)

            # Cross response factors (coupling between surfaces)
            self.cross_response = nn.Parameter(torch.randn(n_surfaces, 1, response_length) * 0.01)

        # Physical constraints will be applied in forward pass

        # Solar gain processing (with thermal mass effects)
        self.solar_absorption = nn.Parameter(torch.tensor([0.7]))  # Absorptance
        self.solar_response = nn.Parameter(torch.randn(1, 1, response_length) * 0.1)

        # Optional: Learn surface temperatures if not measured
        self.estimate_surface_temp = nn.Sequential(
            nn.Linear(3, hidden_dim),  # [T_zone, T_amb, q_hist]
            nn.Tanh(),
            nn.Linear(hidden_dim, 2)  # [T_surf_int, T_surf_ext]
        )

    def generate_response_factors(self, device):
        """
        Generate response factors with appropriate physical constraints
        """
        time_indices = torch.arange(self.response_length, dtype=torch.float32).to(device)

        if self.allow_oscillation:
            # Prony series: sum of decaying exponentials with possible oscillation
            # R(t) = Σ A_i * exp(-λ_i * t) * cos(ω_i * t)

            # Ensure positive decay rates
            ext_decay = torch.abs(self.ext_decay_rates) + 0.1
            int_decay = torch.abs(self.int_decay_rates) + 0.1

            # Generate response factors for each mode
            ext_response = torch.zeros(self.ext_amplitudes.shape[0], 1, self.response_length).to(device)
            int_response = torch.zeros(self.int_amplitudes.shape[0], 1, self.response_length).to(device)

            for i in range(self.n_modes):
                # External response
                decay_envelope = torch.exp(-ext_decay[:, i:i + 1, :] * time_indices.view(1, 1, -1))
                oscillation = torch.cos(self.ext_frequencies[:, i:i + 1, :] * time_indices.view(1, 1, -1))
                ext_response += self.ext_amplitudes[:, i:i + 1, :] * decay_envelope * oscillation

                # Internal response
                decay_envelope = torch.exp(-int_decay[:, i:i + 1, :] * time_indices.view(1, 1, -1))
                oscillation = torch.cos(self.int_frequencies[:, i:i + 1, :] * time_indices.view(1, 1, -1))
                int_response += self.int_amplitudes[:, i:i + 1, :] * decay_envelope * oscillation

            # Apply sign constraints if strict physics enforced
            if self.enforce_strict_physics:
                # External response typically positive (but can oscillate around positive mean)
                ext_response = ext_response + torch.abs(ext_response[:, :, 0:1]) * 0.5
                # Internal response typically negative initially
                int_response = int_response - torch.abs(int_response[:, :, 0:1]) * 0.5

            return ext_response, int_response

        else:
            # Standard monotonic decay
            # Exponential decay envelope - this is a hyperparameter you can tune
            # Typical values: 3-6 hours for light construction, 12-24 hours for heavy
            decay_scale = 6.0  # hours (can make this learnable if desired)
            time_weights = torch.exp(-time_indices / decay_scale)

            if self.enforce_strict_physics:
                # Apply strict physical constraints
                # External response (outside temperature effect) - positive
                ext_response_constrained = torch.abs(self.ext_response) * time_weights.view(1, 1, -1)

                # Internal response (self-response) - negative
                int_response_constrained = -torch.abs(self.int_response) * time_weights.view(1, 1, -1)
            else:
                # Allow learned signs but still enforce decay
                ext_response_constrained = self.ext_response * time_weights.view(1, 1, -1)
                int_response_constrained = self.int_response * time_weights.view(1, 1, -1)

            return ext_response_constrained, int_response_constrained

    def forward(self, T_zone_hist, T_amb_hist, solar_hist, use_surface_estimation=True):
        """
        Args:
            T_zone_hist: (B, T, 1) - Historical zone temperatures
            T_amb_hist: (B, T, 1) - Historical ambient temperatures
            solar_hist: (B, T, 1) - Historical solar radiation
            use_surface_estimation: Whether to estimate surface temperatures

        Returns:
            q_envelope: (B, 1) - Heat flux through envelope at current timestep
            surface_temps: (B, 2) - Estimated surface temperatures (optional)
        """
        B, T, _ = T_zone_hist.shape

        # Generate response factors with physical constraints
        ext_response_constrained, int_response_constrained = self.generate_response_factors(T_zone_hist.device)

        # Solar response is always positive (adding heat) with decay
        time_indices = torch.arange(self.response_length, dtype=torch.float32).to(T_zone_hist.device)
        solar_time_weights = torch.exp(-time_indices / 6.0)
        solar_response_constrained = torch.abs(self.solar_response) * solar_time_weights.view(1, 1, -1)

        if use_surface_estimation:
            # Estimate surface temperatures from zone and ambient
            # Use recent history for estimation
            recent_features = torch.cat([
                T_zone_hist[:, -1:, :],
                T_amb_hist[:, -1:, :],
                solar_hist[:, -1:, :]
            ], dim=-1)

            surface_temps = self.estimate_surface_temp(recent_features.squeeze(1))
            T_surf_int = surface_temps[:, 0:1].unsqueeze(1)  # (B, 1, 1)
            T_surf_ext = surface_temps[:, 1:2].unsqueeze(1)  # (B, 1, 1)

            # Use estimated surface temperatures
            # Pad if necessary
            if T < self.response_length:
                pad_len = self.response_length - T
                T_surf_int_hist = F.pad(T_surf_int.expand(B, T, 1), (0, 0, pad_len, 0))
                T_surf_ext_hist = F.pad(T_surf_ext.expand(B, T, 1), (0, 0, pad_len, 0))
            else:
                # Assume surface temps follow zone/amb with lag
                T_surf_int_hist = 0.9 * T_zone_hist[:, -self.response_length:, :] + 0.1 * T_amb_hist[
                    :, -self.response_length:, :]
                T_surf_ext_hist = 0.3 * T_zone_hist[:, -self.response_length:, :] + 0.7 * T_amb_hist[
                    :, -self.response_length:, :]
        else:
            # Simplified: use zone and ambient as proxies
            T_surf_int_hist = T_zone_hist
            T_surf_ext_hist = T_amb_hist

        # Prepare temperature histories for convolution
        if T < self.response_length:
            pad_len = self.response_length - T
            T_zone_pad = F.pad(T_zone_hist, (0, 0, pad_len, 0))
            T_amb_pad = F.pad(T_amb_hist, (0, 0, pad_len, 0))
            solar_pad = F.pad(solar_hist, (0, 0, pad_len, 0))
        else:
            T_zone_pad = T_zone_hist[:, -self.response_length:, :]
            T_amb_pad = T_amb_hist[:, -self.response_length:, :]
            solar_pad = solar_hist[:, -self.response_length:, :]

        # Reshape for 1D convolution: (B, C, L)
        T_zone_conv = T_zone_pad.transpose(1, 2)  # (B, 1, T)
        T_amb_conv = T_amb_pad.transpose(1, 2)
        solar_conv = solar_pad.transpose(1, 2)

        # Apply response factor convolutions
        # Flip kernels for proper convolution (most recent effect first)
        ext_kernel = torch.flip(ext_response_constrained, dims=[2])
        int_kernel = torch.flip(int_response_constrained, dims=[2])
        solar_kernel = torch.flip(solar_response_constrained, dims=[2])

        # Convolve (using depthwise convolution for multiple surfaces)
        # Heat flux from external temperature history
        q_ext = F.conv1d(T_amb_conv - T_zone_conv, ext_kernel, padding=0)

        # Heat flux from internal temperature history
        q_int = F.conv1d(T_zone_conv - T_amb_conv, int_kernel, padding=0)

        # Solar heat gain (with absorption and thermal mass delay)
        solar_absorbed = solar_conv * torch.sigmoid(self.solar_absorption)
        q_solar = F.conv1d(solar_absorbed, solar_kernel, padding=0)

        # Total heat flux (take last timestep)
        q_total = (q_ext + q_int + q_solar)[:, :, -1]  # (B, n_surfaces)

        # Sum over all surfaces - return (B, 1) to match other modules
        q_envelope = q_total.sum(dim=1, keepdim=True)  # (B, 1)

        if use_surface_estimation:
            return q_envelope, surface_temps
        else:
            return q_envelope, None


class ModNN(nn.Module):
    """
    Modified ModNN with physics-informed envelope module
    """

    def __init__(self, args):
        super(ModNN, self).__init__()
        para = args["para"]
        self.encoLen = args["enLen"]
        self.device = args['device']
        self.window = para["window"]

        # New physics-informed envelope module
        self.Ext = PhysicsInformedEnvelope(
            n_surfaces=para.get("n_surfaces", 1),
            response_length=para.get("response_length", 24),
            hidden_dim=para.get("envelope_hidden", 16)
        )

        # Keep other modules the same
        self.Zone = zone(para["Zone_in"], para["Zone_out"])
        self.HVAC = hvac(para["HVAC_in"], para["HVAC_out"])
        self.Int = internal(para["Int_in"], para["Int_h"], para["Int_out"])

    def forward(self, input_X):
        """
        input_X order: [T_zone, T_ambient, solar, day_sin, day_cos, occ, phvac]
        Shape: [batch_size, time_steps, features]
        """
        T_zone_X = input_X[:, :, [0]]  # Zone temperature
        T_amb_X = input_X[:, :, [1]]  # Ambient temperature
        Solar_X = input_X[:, :, [2]]  # Solar radiation
        Int_X = input_X[:, :, [3, 4, 5]]  # Sin/Cos + Occupancy
        HVAC_X = input_X[:, :, [6]]  # HVAC power input

        # Initialize outputs
        B, T, _ = input_X.shape
        TOut_list = torch.zeros(B, T, 1).to(self.device)
        HVAC_list = torch.zeros_like(HVAC_X).to(self.device)
        Ext_list = torch.zeros_like(HVAC_X).to(self.device)
        Int_list = torch.zeros_like(HVAC_X).to(self.device)
        deltaQ_list = torch.zeros_like(HVAC_X).to(self.device)

        window_size = self.window

        # Initialize with measured temperatures
        for i in range(window_size):
            TOut_list[:, i, :] = T_zone_X[:, i, :]
            HVAC_list[:, i, :] = HVAC_X[:, i, :]

        E_Zone_T = T_zone_X[:, [[window_size]], :]

        # --- Encoding Phase ---
        for i in range(window_size, self.encoLen):
            TOut_list[:, i:i + 1, :] = E_Zone_T  # Keep 3D shape

            # Use physics-informed envelope module
            # Provide history up to current timestep
            T_zone_hist = TOut_list[:, max(0, i - self.Ext.response_length + 1):i + 1, :]
            T_amb_hist = T_amb_X[:, max(0, i - self.Ext.response_length + 1):i + 1, :]
            Solar_hist = Solar_X[:, max(0, i - self.Ext.response_length + 1):i + 1, :]

            ext_flux, _ = self.Ext(T_zone_hist, T_amb_hist, Solar_hist)
            ext_flux = ext_flux.unsqueeze(1)  # (B, 1, 1)

            # Other heat sources
            hvac_flux = self.HVAC(HVAC_X[:, i:i + 1, :])
            int_flux = self.Int(Int_X[:, i:i + 1, :])

            total_flux = ext_flux + hvac_flux + int_flux

            # Store fluxes
            HVAC_list[:, i:i + 1, :] = hvac_flux  # Keep 3D shape
            Ext_list[:, i:i + 1, :] = ext_flux  # Keep 3D shape
            Int_list[:, i:i + 1, :] = int_flux  # Keep 3D shape
            deltaQ_list[:, i:i + 1, :] = total_flux  # Keep 3D shape

            # Zone temperature dynamics
            deltaT = self.Zone(total_flux)
            E_Zone_T = T_zone_X[:, i:i + 1, :] + deltaT

        # --- Decoding Phase ---
        for i in range(self.encoLen, T):
            TOut_list[:, i:i + 1, :] = E_Zone_T  # Keep 3D shape

            # Use physics-informed envelope module
            T_zone_hist = TOut_list[:, max(0, i - self.Ext.response_length + 1):i + 1, :]
            T_amb_hist = T_amb_X[:, max(0, i - self.Ext.response_length + 1):i + 1, :]
            Solar_hist = Solar_X[:, max(0, i - self.Ext.response_length + 1):i + 1, :]

            ext_flux, _ = self.Ext(T_zone_hist, T_amb_hist, Solar_hist)
            ext_flux = ext_flux.unsqueeze(1)

            hvac_flux = self.HVAC(HVAC_X[:, i:i + 1, :])
            int_flux = self.Int(Int_X[:, i:i + 1, :])

            total_flux = ext_flux + hvac_flux + int_flux

            # Store fluxes
            HVAC_list[:, i:i + 1, :] = hvac_flux  # Keep 3D shape
            Ext_list[:, i:i + 1, :] = ext_flux  # Keep 3D shape
            Int_list[:, i:i + 1, :] = int_flux  # Keep 3D shape
            deltaQ_list[:, i:i + 1, :] = total_flux  # Keep 3D shape

            # Update temperature
            deltaT = self.Zone(total_flux)
            E_Zone_T = E_Zone_T + deltaT

        return TOut_list, HVAC_list, (Ext_list, Int_list, deltaQ_list)
