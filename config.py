community_token = "vk1.a.0YbeAPGAzDA6iZjz8mtXMmFXL6gi5z92c0LlLp1COnNA0ESflmch5i6OJDwWejrrxO-GTQNwXfJ8yWDqEHIe3CE-vSAmdfDt25JHmoH525nspXK4y-4kvvYlgE8bYKvj-bJ0247t_bt1lkL61sFX6ugE_7d_SavGLWaInVg1EkIvhYqA2N__szNAACFCCDNVAc1HR9wO_k-MYERogfptHw"
access_token = "vk1.a.F4wPX1ULcn2VmzFFtncwIZel341pwf761epAjpMn_onbZ4o5CqsB8CspYFvwEt0v7o8p2WSh_oY_X84YJ35bOVMzXgfqAVRJw-1bjdYbujhU16weUM3_TFlIuG4SXVqPhQeoUsPyCrl3WRrR9WOloPy2ajarusDMCkszzyhG84HUQV9XCuH-cyARd2xlGiEp"
service_token = "3ce665873ce665873ce665879c3ff2ff0833ce63ce66587587605ad574b1dfc9a0ff71b"
db_name = "vkinder"
db_username = "postgres"
db_password = open("db_password.txt", "r").read()
db_url_object = f"postgresql+psycopg2://{db_username}:{db_password}@localhost/{db_name}"